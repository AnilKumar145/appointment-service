pipeline {
  agent any
  
  tools {
    // This requires the Jenkins Chocolatey plugin to be installed
    chocolatey 'choco'
  }

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

    stage('Install Python') {
      steps {
        script {
          echo 'Installing Python using Chocolatey...'
          
          // Install Python 3.11 using Chocolatey
          bat '''
            @echo off
            choco --version || (
              echo Installing Chocolatey...
              Set-ExecutionPolicy Bypass -Scope Process -Force
              [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
              iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
              refreshenv
            )
            
            echo Installing Python 3.11...
            choco install python311 -y --no-progress --version=3.11.9
            
            echo Refreshing environment variables...
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            echo Verifying Python installation...
            python --version
            python -c "import sys; print(sys.executable)"
          '''
          
          // Set Python path variables
          env.PYTHON = 'python'
          env.PIP = 'python -m pip'
        }
      }
    }
    
    stage('Setup Python Environment') {
      steps {
        script {
          echo 'Setting up Python environment...'
          
          // Create virtual environment
          try {
            bat """
              python -m venv ${VENV_PATH}
              ${VENV_PATH}\\Scripts\\pip install --upgrade pip setuptools wheel
              ${VENV_PATH}\\Scripts\\pip install -r requirements.txt
              ${VENV_PATH}\\Scripts\\pip install -r requirements-dev.txt
            """
          } catch (Exception e) {
            error("Failed to set up Python environment: ${e.message}")
          }
          
          // Verify the virtual environment works
          try {
            bat "${VENV_PATH}\\Scripts\\python -c \"import sys; print('Python version:', sys.version)\""
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
