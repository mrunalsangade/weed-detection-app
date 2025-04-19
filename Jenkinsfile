pipeline {
  agent any

  environment {
    DOCKERHUB_CRED = 'f4bb4469-7e31-4cfc-a752-062d8c99b139'
  }

  stages {
    stage('Install Dependencies') {
      steps {
        bat 'python -m pip install --upgrade pip'
        bat 'python -m pip install -r requirements.txt'
      }
    }

    stage('Build') {
      steps {
        bat 'echo No build step required'
      }
    }

    stage('Test') {
      steps {
        bat 'if not exist reports mkdir reports'
        bat 'python -m pytest --junitxml=reports/results.xml'
      }
      post {
        always {
          junit 'reports/*.xml'
        }
      }
    }

    stage('Docker Info') {
      steps {
        bat 'docker version'
        bat 'docker info'
      }
    }

    stage('Docker Build & Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: "${DOCKERHUB_CRED}",
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
          bat 'docker build -t %DOCKER_USER%/weed-detection-app:latest .'
          bat 'docker push %DOCKER_USER%/weed-detection-app:latest'
        }
      }
    }
  }

  post {
    success { echo '✅ Pipeline succeeded' }
    failure { echo '❌ Pipeline failed' }
  }
}
