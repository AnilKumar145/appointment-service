pipeline {
  agent any

  environment {
    // Environment Variables
    DOCKER_IMAGE = 'appointment-service'
    DOCKER_TAG = "${env.BUILD_NUMBER}"
    VENV_PATH = "${WORKSPACE}/venv"
    PYTHON = "${VENV_PATH}/Scripts/python"
    PIP = "${VENV_PATH}/Scripts/pip"
    
    // Credentials (stored in Jenkins Credentials Store)
    DOCKERHUB_CREDENTIALS = credentials('docker-hub-credentials')
    
    // Environment-specific configurations
    ENV_FILE = '.env.test'  // Default to test environment
  }

  options {
    // Discard old builds to save space
    buildDiscarder(logRotator(numToKeepStr: '10'))
    // Timeout after 30 minutes
    timeout(time: 30, unit: 'MINUTES')
    // Add timestamps to console output
    timestamps()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: '*/main']],
          userRemoteConfigs: [[url: 'https://github.com/AnilKumar145/appointment-service.git']],
          extensions: [[$class: 'CleanBeforeCheckout']]
        ])
      }
    }

    stage('Setup Python Environment') {
      steps {
        script {
          // Create virtual environment
          bat """
            python -m venv ${VENV_PATH}
            ${PIP} install --upgrade pip setuptools wheel
            ${PIP} install -r requirements.txt
            ${PIP} install -r requirements-dev.txt
          """
        }
      }
    }

    stage('Code Quality & Linting') {
      parallel {
        stage('Run Flake8') {
          steps {
            script {
              bat "${PYTHON} -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
              bat "${PYTHON} -m flake8 . --count --max-complexity=10 --max-line-length=127 --statistics"
            }
          }
        }
        
        stage('Run Black') {
          steps {
            script {
              bat "${PYTHON} -m black --check --diff --color ."
            }
          }
        }
        
        stage('Run Isort') {
          steps {
            script {
              bat "${PYTHON} -m isort --check-only --diff ."
            }
          }
        }
      }
    }

    stage('Security Scanning') {
      parallel {
        stage('Bandit Security Scan') {
          steps {
            script {
              bat "${PYTHON} -m bandit -r . -c pyproject.toml"
            }
          }
        }
        
        stage('Dependency Check') {
          steps {
            script {
              bat "${PIP} install safety"
              bat "safety check --full-report"
            }
          }
        }
      }
    }

    stage('Unit Tests') {
      steps {
        script {
          // Run unit tests with coverage
          bat """
            ${PYTHON} -m pytest tests/unit \
              --cov=app \
              --cov-report=xml:coverage.xml \
              --cov-report=term \
              -v \
              --junitxml=test-results/unit-tests.xml
          """
        }
      }
      post {
        always {
          // Publish test results
          junit 'test-results/unit-tests.xml'
          // Publish coverage report
          publishHTML(target: [
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: true,
            reportDir: 'htmlcov',
            reportFiles: 'index.html',
            reportName: 'Coverage Report'
          ])
        }
      }
    }

    stage('Integration Tests') {
      steps {
        script {
          // Start test containers
          bat 'docker-compose -f docker-compose.test.yml up -d --build'
          
          // Wait for services to be ready
          bat """
            ${PYTHON} -m pytest tests/integration \
              -v \
              --junitxml=test-results/integration-tests.xml
          """
        }
      }
      post {
        always {
          // Stop test containers
          bat 'docker-compose -f docker-compose.test.yml down --volumes --remove-orphans'
          // Publish test results
          junit 'test-results/integration-tests.xml'
        }
      }
    }

    stage('Build Docker Image') {
      when {
        branch 'main'  // Only build for main branch
      }
      steps {
        script {
          // Build and tag the Docker image
          docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-credentials') {
            def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
            // Push to Docker Hub
            image.push()
            // Also tag as 'latest' for the main branch
            if (env.BRANCH_NAME == 'main') {
              image.push('latest')
            }
          }
        }
      }
    }

    stage('Deploy to Staging') {
      when {
        branch 'main'  // Only deploy to staging from main branch
      }
      steps {
        script {
          // Deploy to staging environment
          withEnv(['ENV_FILE=.env.staging']) {
            // Stop and remove old containers
            bat 'docker-compose -f docker-compose.staging.yml down --remove-orphans'
            
            // Pull and start new containers
            bat 'docker-compose -f docker-compose.staging.yml pull'
            bat 'docker-compose -f docker-compose.staging.yml up -d'
            
            // Run database migrations
            bat 'docker-compose -f docker-compose.staging.yml exec app alembic upgrade head'
          }
        }
      }
    }
  }

  post {
    always {
      node('built-in') {
        script {
          try {
            // Clean up workspace
            cleanWs()
            
            // Clean up Docker resources
            withCredentials([usernamePassword(
              credentialsId: 'docker-hub-credentials',
              usernameVariable: 'DOCKER_USER',
              passwordVariable: 'DOCKER_PASS'
            )]) {
              bat 'docker system prune -f --volumes'
            }
          } catch (Exception e) {
            echo 'Failed to clean up Docker resources: ' + e.toString()
          }
        }
      }
    }
    
    success {
      node('built-in') {
        script {
          if (env.BRANCH_NAME == 'main') {
            // Notify success (e.g., Slack, email)
            echo '✅ Pipeline succeeded!'
          }
        }
      }
    }
    
    failure {
      node('built-in') {
        script {
          try {
            // Notify failure (e.g., Slack, email)
            echo '❌ Pipeline failed!'
            
            // Archive artifacts for debugging
            archiveArtifacts artifacts: '**/test-results/**/*.xml', allowEmptyArchive: true
            archiveArtifacts artifacts: '**/coverage.xml', allowEmptyArchive: true
          } catch (Exception e) {
            echo 'Error in failure handling: ' + e.toString()
          }
        }
      }
    }
    
    cleanup {
      node('built-in') {
        script {
          try {
            // Clean up Docker resources
            withCredentials([usernamePassword(
              credentialsId: 'docker-hub-credentials',
              usernameVariable: 'DOCKER_USER',
              passwordVariable: 'DOCKER_PASS'
            )]) {
              bat 'docker-compose down --remove-orphans || echo "No containers to stop"'
              bat 'docker system prune -f --volumes || echo "No Docker resources to clean"'
            }
          } catch (Exception e) {
            echo 'Error during cleanup: ' + e.toString()
          }
        }
      }
    }
  }
}
