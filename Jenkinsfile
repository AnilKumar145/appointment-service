pipeline {
    agent {
        docker {
            image 'python:3.10-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    environment {
        PYTHONUNBUFFERED = '1'
        TEST_DATABASE_URL = 'postgresql://postgres:anil@postgres:5432/appointment_test_db'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Set up Python') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Lint') {
            steps {
                sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
                sh 'flake8 . --count --max-complexity=10 --max-line-length=127 --statistics'
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh 'pytest tests/unit/ -v --cov=app --cov-report=xml'
                junit '**/test-reports/*.xml'
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
        
        stage('Integration Tests') {
            environment {
                DB_HOST = 'postgres'
            }
            options {
                timeout(time: 15, unit: 'MINUTES')
            }
            steps {
                script {
                    try {
                        sh 'docker-compose -f docker-compose.test.yml up -d postgres'
                        sh 'sleep 10' // Wait for DB to start
                        sh 'pytest tests/integration/ -v'
                    } finally {
                        sh 'docker-compose -f docker-compose.test.yml down'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def version = sh(script: 'git describe --tags --always', returnStdout: true).trim()
                    docker.build("appointment-service:${version}")
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                dir('k8s/staging') {
                    sh 'kubectl apply -k .'
                }
            }
        }
    }
    
    post {
        always {
            // Clean up
            sh 'docker-compose -f docker-compose.test.yml down --remove-orphans'
            cleanWs()
        }
        success {
            // Notify success
            slackSend(color: 'good', message: "Build Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            // Notify failure
            slackSend(color: 'danger', message: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
    }
}