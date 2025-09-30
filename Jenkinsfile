pipeline {
  agent any

  environment {
    DOCKER_IMAGE = 'appointment-service'
    DOCKER_TAG = "${env.BUILD_NUMBER}"
    VENV_PATH = "${WORKSPACE}\\venv"
    PYTHON = "${VENV_PATH}\\Scripts\\python"
    PIP = "${VENV_PATH}\\Scripts\\pip"
    ENV_FILE = '.env.test'
    // Set UTF-8 encoding for all Python processes
    PYTHONIOENCODING = 'utf-8'
    PYTHONUNBUFFERED = '1'
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timeout(time: 30, unit: 'MINUTES')
    timestamps()
    // Allow the build to continue even if a stage fails
    skipStagesAfterUnstable()
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
          
          // Create and activate virtual environment using system Python directly
          try {
            // Create virtual environment
            bat """
              python -m venv "${VENV_PATH}"
              call "${VENV_PATH}\\Scripts\\activate.bat"
              
              echo [INFO] Upgrading pip, setuptools and wheel...
              python -m pip install --upgrade pip setuptools wheel
              
              echo [INFO] Installing project dependencies...
              pip install -r requirements.txt
              
              echo [INFO] Installing development dependencies...
              pip install -r requirements-dev.txt
              
              echo [INFO] Installed packages:
              pip list
            """
            
            // Verify the virtual environment works
            def pythonVersion = bat(script: "\"${PYTHON}\" --version", returnStdout: true).trim()
            echo "Virtual environment Python version: ${pythonVersion}"
            
          } catch (Exception e) {
            error("Failed to set up Python environment: ${e.message}")
          }
          
          echo '✅ Python environment setup completed successfully.'
        }
      }
    }

    stage('Verify Dependencies') {
      steps {
        script {
          echo 'Verifying test dependencies...'
          bat """
            call "${VENV_PATH}\\Scripts\\activate.bat"
            python -c "import pytest_cov; print('✅ pytest-cov available')"
            python -c "import coverage; print('✅ coverage available')"
            python -c "import pytest; print(f'✅ pytest {pytest.__version__} available')"
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
              echo 'Running Bandit security scan...'
              
              // Create reports directory if it doesn't exist
              bat "if not exist \"${WORKSPACE}\\reports\" mkdir \"${WORKSPACE}\\reports\""
              
              // Run Bandit with error handling
              catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                bat """
                  call "${VENV_PATH}\\Scripts\\activate.bat"
                  
                  echo [INFO] Installing/updating bandit...
                  pip install --upgrade bandit
                  
                  echo [INFO] Running Bandit scan...
                  bandit -r . \
                    -f json -o "${WORKSPACE}\\reports\\bandit-report.json" \
                    -ll -c .bandit \
                    || echo 'Bandit scan completed with findings (non-blocking)'
                    
                  type "${WORKSPACE}\\reports\\bandit-report.json"
                """
              }
            }
          }
          post {
            always {
              // Archive the Bandit report
              archiveArtifacts artifacts: 'reports/bandit-report.json', allowEmptyArchive: true
            }
          }
        }
        
        stage('Dependency Check') {
          steps {
            script {
              echo 'Running dependency vulnerability scan...'
              
              // Run Safety with error handling
              catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                bat """
                  call "${VENV_PATH}\\Scripts\\activate.bat"
                  
                  echo [INFO] Running dependency scan...
                  safety check --json --output "${WORKSPACE}\\reports\\safety-report.json" || echo "Safety scan completed with findings"
                """
              }
            }
          }
          post {
            always {
              // Archive the Safety report
              archiveArtifacts artifacts: 'reports/safety-report.json', allowEmptyArchive: true
            }
          }
        }
      }
    }

    stage('Unit Tests') {
      steps {
        script {
          // Create test-results directory first
          bat "if not exist \"${WORKSPACE}\\test-results\" mkdir \"${WORKSPACE}\\test-results\""
          
          bat """
            ${PYTHON} -m pytest tests/unit --cov=app --cov-report=xml:coverage.xml --cov-report=term -v --junitxml=test-results/unit-tests.xml
          """
        }
      }
      post {
        always {
          junit 'test-results/unit-tests.xml'
          // Archive coverage report
          archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
        }
      }
    }

    stage('Integration Tests') {
      steps {
        script {
          bat "if not exist \"${WORKSPACE}\\test-results\" mkdir \"${WORKSPACE}\\test-results\""
          bat 'docker-compose -f docker-compose.test.yml up -d --build'
          bat """
            ${PYTHON} -m pytest tests/integration -v --junitxml=test-results/integration-tests.xml
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
      script {
        echo "Build completed with status: ${currentBuild.currentResult}"
        
        // Archive test results and reports
        archiveArtifacts artifacts: '**/test-results/**/*, **/reports/**/*, **/*.xml, **/*.json, **/*.html', 
                       allowEmptyArchive: true
        
        // Clean up workspace
        cleanWs(cleanWhenAborted: true, cleanWhenFailure: true, cleanWhenNotBuilt: true, 
               cleanWhenSuccess: true, cleanupMatrixParent: true, deleteDirs: true)
      }
    }
    
    success {
      script {
        if (env.BRANCH_NAME == 'main') {
          echo '✅ Pipeline succeeded! Deployment completed.'
        } else {
          echo '✅ Pipeline succeeded!'
        }
      }
    }
    
    failure {
      script {
        echo '❌ Pipeline failed! Check the logs for details.'
        
        // Archive additional debug information
        bat 'echo "=== System Information ===" && systeminfo'
        bat 'echo "=== Python Version ===" && python --version || echo "Python not found"'
        bat 'echo "=== Pip Version ===" && pip --version || echo "Pip not found"'
        
        // Try to get more detailed error information
        try {
          if (fileExists("${WORKSPACE}\\reports\\bandit-report.json")) {
            echo 'Bandit report summary:'
            bat "type \"${WORKSPACE}\\reports\\bandit-report.json\" | findstr /i \"issue\" || echo No issues found"
          }
          
          if (fileExists("${WORKSPACE}\\reports\\safety-report.json")) {
            echo 'Safety report summary:'
            bat "type \"${WORKSPACE}\\reports\\safety-report.json\" | findstr /i \"vulnerability\" || echo No vulnerabilities found"
          }
        } catch (Exception e) {
          echo 'Error while generating failure report: ' + e.toString()
        }
      }
    }
    
    cleanup {
      script {
        echo 'Cleaning up Docker resources...'
        try {
          bat 'docker-compose down --remove-orphans || echo No Docker Compose running'
          bat 'docker system prune -f || echo Docker prune completed'
        } catch (Exception e) {
          echo 'Cleanup warning: ' + e.message
        }
      }
    }
  }
}