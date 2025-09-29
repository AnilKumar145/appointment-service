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
            script {
                // Force remove any running containers
                bat 'docker-compose down --remove-orphans || echo "No containers to stop"'
                
                // Kill any process using port 5433
                bat '''
                    @echo off
                    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5433') do (
                        taskkill /F /PID %%a
                    )
                    if errorlevel 1 (
                        echo No process found on port 5433
                        exit 0
                    )
                '''
            }
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
