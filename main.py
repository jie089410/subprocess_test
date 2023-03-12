#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: haojie-li
@contact: 15036425579@163.com
@time: 2023/3/4 21:06
@file: main.py
@desc: 
"""
import random
import shlex
import subprocess
import sys
import threading
import yaml
import time
import logging
from kazoo.client import KazooClient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(thread)d - %(message)s')
logger = logging.getLogger(__name__)


def read_output_from_subprocess(process: subprocess.Popen, zk: KazooClient, pid: int):
    while process.poll() is None:
        line = process.stdout.readline()
        line = line.strip()
        if line:
            logger.info('进程{} Subprogram output: [{}]'.format(pid, line))
    if process.returncode == 0:
        logger.info('进程{} Subprogram success'.format(pid))
    else:
        logger.error('进程{} Subprogram failed'.format(pid))
    # 释放zookeeper连接
    zk.stop()


def run_test(to_test_nodes_num: int, test_cases: list, available_nodes: set):
    # 存放读取子进程输出的线程
    read_threads = []
    for test_case in test_cases:
        test_time = random.randint(10, 20)
        shell_cmd = 'sh test.sh {} {}'.format(test_time, test_case)
        cmd = shlex.split(shell_cmd)
        # 执行每条case前，建立zk连接, 预定机器
        zk = KazooClient(hosts="192.168.0.212:2181")
        zk.start()
        lock = zk.Lock("/nodes")
        reserve_completed = False
        while not reserve_completed:
            with lock:
                # 查询已经被使用的node
                used_nodes = set(zk.get_children("/nodes"))
                if len(available_nodes - used_nodes) >= to_test_nodes_num:
                    for index, node in enumerate(available_nodes - used_nodes):
                        zk.create("/nodes/{}".format(node), ephemeral=True)
                        if index + 1 == to_test_nodes_num:
                            # 预定到足够的机器，跳出for循环，开始进行用例测试
                            break
                    # 预定到足够的机器，开启子进程运行测试
                    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         encoding='utf-8')
                    # 子进程开始测试后，立即开启线程去读取子进程的输出
                    th = threading.Thread(target=read_output_from_subprocess, args=(p, zk, p.pid))
                    th.start()
                    read_threads.append(th)
                else:
                    time.sleep(1)
                    logger.info("{}没有足够的节点用于测试, 等待其他测试完成释放节点".format(test_case))
                    # 跳出while循环，继续下一轮等待
                    continue
            # 预定够机器后，一条case在子进程运行，更改reserve_completed状态，开始下条case的预定机器过程
            reserve_completed = True

    for th in read_threads:
        # 阻塞读取子进程输出线程，使得子进程输出完全读取
        # 似乎，因为读取函数里，有使用while循环，这里不阻塞线程，主进程也不会立即结束
        th.join()


if __name__ == '__main__':
    to_test_nodes_num = int(sys.argv[1])
    test_cases = sys.argv[2].split("-")
    available_nodes = None
    with open("./config.yaml") as f:
        nodes_dict = yaml.safe_load(f)
        available_nodes = set(nodes_dict.get("Machines"))

    run_test(to_test_nodes_num, test_cases, available_nodes)
