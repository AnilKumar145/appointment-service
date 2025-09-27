pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        // Pull your code from GitHub
        checkout scm
      }
    }

    stage('Stop old containers') {
      steps {
        // Stop any previously running containers
        bat 'docker compose down || docker-compose down'
      }
    }

    stage('Build & Start containers') {
      steps {
        // Build and start fresh containers
        bat 'docker compose up -d --build || docker-compose up -d --build'
      }
    }

    stage('Verify Running Containers') {
      steps {
        // Show running containers
        bat 'docker ps'
        // Show last logs
        bat 'docker compose logs --no-color --tail 20 || docker-compose logs --tail 20'
      }
    }
  }

  post {
    success {
      echo '✅ Deployment successful! Check http://localhost:8007'
    }
    failure {
      echo '❌ Deployment failed. Check console output.'
    }
  }
}
