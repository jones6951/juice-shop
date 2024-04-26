pipeline {
  agent any

  environment {
    PROJECT = 'juice-shop'
    VERSION = '16.0.1'
    BRANCH = 'main'
    BLACKDUCK_ACCESS_TOKEN = credentials('blackduck-token')
    SRM_TOKEN = credentials('srm-token')
  }

  stages{
    stage('NPM Install') {
      steps {
        sh 'npm install'
      }
    }

    stage ('Security Testing') {
      parallel {
        stage('SAST - Coverity') {
          steps {
            sh '''
              echo "Running SAST Testing"
            '''
          }
        }
        stage ('SCA - Black Duck') {
          steps {
            sh '''
              echo "Running BlackDuck"
              rm -fr /tmp/detect9.sh
              curl -s -L https://detect.synopsys.com/detect9.sh > /tmp/detect9.sh
              bash /tmp/detect9.sh --blackduck.url="${BLACKDUCK_URL}" --blackduck.api.token="${BLACKDUCK_ACCESS_TOKEN}" --detect.project.name="${PROJECT}" --detect.project.version.name="${VERSION}" --blackduck.trust.cert=true
            '''
          }
        }
      }
    }

    stage ('SRM') {
      agent { label 'ubuntu' }
      steps {
        sh '''
          echo "Running SRM"
        '''
      }
    }
    stage('Clean Workspace') {
      agent { label 'ubuntu' }
      steps {
        cleanWs()
      }
    }
  }
}
