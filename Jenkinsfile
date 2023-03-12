pipeline {
  agent any
  parameters {
        string(name: 'node_num', defaultValue: '1', description: '模拟测试需要的节点数')
        string(name: 'cases', defaultValue: 'case1-case2-case3', description: '模拟需要测试的用例，格式为case1-case2-case3')
    }
  stages {
    stage('Artifactory-config download') {
      steps {
        rtDownload (
                serverId: 'config_artifactory',
                spec: '''{
                    "files": [
                        {
                        "pattern": "my_local_repo/config.yaml",
                        "target": "${WORKSPACE}/"
                        },
                        {
                        "pattern": "my_local_repo/test.sh",
                        "target": "${WORKSPACE}/"
                        }
                    ]
                }''',
            )
      }
    }
    stage('运行测试') {
        steps{
            sh "python3 -u main.py ${node_num} ${cases}"
        }
    }
  }
}