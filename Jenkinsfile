pipeline {
  agent any
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

  }
}