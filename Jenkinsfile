pipeline {
    agent any
    parameters {
        string defaultValue: 'workload1;workload2;workload3', description: '请输入要构建的多个workload名字，以;隔开', name: 'workloads', trim: true
        booleanParam defaultValue: true, description: '是否从项目中生成需要构建的workloads', name: 'generate_workloads_from_code'
    }
    stages {
        stage('获取要测试的workloads') {
            steps {
                script {
                    if (generate_workloads_from_code) {
                        workloads = sh(script: "ls ${WORKSPACE}/workloads", returnStdout: true).trim().replace('\n', ';')
                    }
                }
            }
        }
        stage('测试workloads'){
            steps{
                script{
                    def jobs = [:]
                    for (workload in workloads.tokenize(';')) {
                        def workload_temp = workload
                        jobs["${workload_temp}"] = {
                            build quietPeriod: 2, job: '/single_workload', parameters: [
                              string(name: 'workload', value: "${workload_temp}"),
                              string(name: 'node_num', value: '1'),
                              string(name: 'cases', value: 'case1-case2-case3'),
                              booleanParam(name: 'all_cases', value: true)]
                        }
                    }
                    parallel jobs
                }
            }
        }
    }
}