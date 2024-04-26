pipeline {
  agent any

  environment {
    PROJECT = 'juice-shop'
    VERSION = '1.0'
    BRANCH = 'main'
    BLACKDUCK_ACCESS_TOKEN = credentials('blackduck-token')
    SRM_TOKEN = credentials('srm-token')
    GITHUB_TOKEN = credentials('github-token')
  }

  stages{
    stage('NPM Install') {
      steps {
        sh 'npm install'
      }
    }

    stage('Set Up Environment') {
      steps {
        sh '''
          curl -s -L https://raw.githubusercontent.com/jones6951/io-scripts/main/getProjectID.sh > /tmp/getProjectID.sh
          curl -s -L https://raw.githubusercontent.com/jones6951/io-scripts/main/isNumeric.sh > /tmp/isNumeric.sh

          chmod +x /tmp/getProjectID.sh
          chmod +x /tmp/isNumeric.sh
        '''
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
          projectID=$(/tmp/getProjectID.sh --url=${CODEDX_SERVER_URL} --apikey=${CODEDX_TOKEN} --project=${PROJECT})
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
