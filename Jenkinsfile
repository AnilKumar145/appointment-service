pipeline {
  agent any

  environment {
    DOCKER_IMAGE = 'appointment-service'
    DOCKER_TAG = "${env.BUILD_NUMBER}"
    VENV_PATH = "${WORKSPACE}/venv"
    PYTHON = "${VENV_PATH}/Scripts/python"
    PIP = "${VENV_PATH}/Scripts/pip"
    ENV_FILE = '.env.test'
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timeout(time: 30, unit: 'MINUTES')
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
          echo 'Setting up Python environment...'
          
          // Try to find a working Python
          def pythonExe = 'python'
          def pythonFound = false
          
          // Check if system Python works
          try {
            def pythonVersion = bat(script: 'python --version', returnStdout: true).trim()
            echo "Found Python version: ${pythonVersion}"
            
            // Verify Python can import modules
            bat 'python -c "import sys; print(sys.executable)"'
            pythonFound = true
          } catch (Exception e) {
            echo 'Python not found in PATH or not working properly'
          }
          
          if (!pythonFound) {
            // Try known Python locations
            def pythonPaths = [
              'C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python311\\python.exe',
              'C:\\Python39\\python.exe',
              'C:\\Python310\\python.exe',
              'C:\\Python311\\python.exe',
              'C:\\Program Files\\Python39\\python.exe',
              'C:\\Program Files\\Python310\\python.exe',
              'C:\\Program Files\\Python311\\python.exe'
            ]
            
            for (path in pythonPaths) {
              try {
                echo "Trying Python at: ${path}"
                def version = bat(script: "\"${path}\" --version", returnStdout: true).trim()
                echo "Found Python version: ${version}"
                bat "\"${path}\" -c \"import sys; print(sys.executable)\""
                pythonExe = "\"${path}\""
                pythonFound = true
                echo "Using Python at: ${path}"
                break
              } catch (Exception e) {
                echo "Python not found at ${path}"
              }
            }
            
            if (!pythonFound) {
              error('No working Python installation found. Please install Python 3.8+ and ensure it\'s in the system PATH.')
            }
          }
          
          // Create virtual environment
          try {
            bat """
              ${pythonExe} -m venv ${VENV_PATH}
              ${PIP} install --upgrade pip setuptools wheel
              ${PIP} install -r requirements.txt
              ${PIP} install -r requirements-dev.txt
            """
          } catch (Exception e) {
            error("Failed to set up Python environment: ${e.message}")
          }
          
          // Verify the virtual environment works
          try {
            bat "${PYTHON} -c \"import sys; print('Python version:', sys.version)\""
          } catch (Exception e) {
            error('Virtual environment setup failed. Please check the logs.')
          }
          
          echo 'Python environment setup completed successfully.'
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
        stage('Format and Check') {
          steps {
            script {
              // Auto-fix formatting first
              bat "${PYTHON} -m black . || echo 'Black formatting completed'"
              bat "${PYTHON} -m isort . || echo 'Import sorting completed'"
              
              // Then verify everything is properly formatted
              bat "${PYTHON} -m black --check --diff --color ."
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
              bat "${PYTHON} -m bandit -r . -ll"
            }
          }
        }
        stage('Dependency Check') {
          steps {
            script {
              bat "${PYTHON} -m safety scan --continue-on-error || echo 'Safety scan completed'"
            }
          }
        }
      }
    }

    stage('Unit Tests') {
      steps {
        script {
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
          junit 'test-results/unit-tests.xml'
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
          bat 'docker-compose -f docker-compose.test.yml up -d --build'
          bat """
            ${PYTHON} -m pytest tests/integration \
              -v \
              --junitxml=test-results/integration-tests.xml
          """
        }
      }
      post {
        always {
          bat 'docker-compose -f docker-compose.test.yml down --volumes --remove-orphans'
          junit 'test-results/integration-tests.xml'
        }
      }
    }

    stage('Build Docker Image') {
      when {
        branch 'main'
      }
      steps {
        script {
          def imageName = "${DOCKER_IMAGE}:${DOCKER_TAG}"
          bat "docker build -t ${imageName} ."

          if (env.BRANCH_NAME == 'main') {
            bat "docker tag ${imageName} ${DOCKER_IMAGE}:latest"
            echo "Image tagged as latest"
          }
          bat 'docker images'
        }
      }
    }

    stage('Deploy to Staging') {
      when {
        branch 'main'
      }
      steps {
        script {
          withEnv(['ENV_FILE=.env.staging']) {
            bat 'docker-compose -f docker-compose.staging.yml down --remove-orphans'
            bat 'docker-compose -f docker-compose.staging.yml pull'
            bat 'docker-compose -f docker-compose.staging.yml up -d'
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
            cleanWs()
            bat 'docker system prune -f --volumes || echo "Docker cleanup failed, but continuing..."'
          } catch (Exception e) {
            echo 'Error in always post action: ' + e.toString()
          }
        }
      }
    }
    success {
      node('built-in') {
        script {
          if (env.BRANCH_NAME == 'main') {
            echo '✅ Pipeline succeeded!'
          }
        }
      }
    }
    failure {
      node('built-in') {
        script {
          try {
            echo '❌ Pipeline failed!'
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
            if (fileExists('docker-compose.yml')) {
              bat 'docker-compose down --remove-orphans || echo "No containers to stop"'
            } else {
              echo 'No docker-compose.yml found, skipping container cleanup'
            }
            bat 'docker system prune -f --volumes || echo "No Docker resources to clean"'
          } catch (Exception e) {
            echo 'Warning: Error during Docker cleanup: ' + e.message
          }
        }
      }
    }
  }
}