#!/bin/bash
test_time=$1
test_case=$2
while [ $test_time -gt 0 ]
do
  echo "正在测试: $test_case"
  sleep 1
  let test_time--
done