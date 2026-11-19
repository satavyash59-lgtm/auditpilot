pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        REPO = 'auditpilot'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build image') {
            steps {
                script {
                    env.ACCOUNT_ID = sh(
                        returnStdout: true,
                        script: 'aws sts get-caller-identity --query Account --output text'
                    ).trim()

                    env.REGISTRY = "${env.ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"
                    env.IMAGE = "${env.REGISTRY}/${env.REPO}"
                }

                sh '''
                    docker build \
                    -t $IMAGE:$BUILD_NUMBER \
                    -t $IMAGE:latest .
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    docker run --rm \
                    --entrypoint python \
                    $IMAGE:$BUILD_NUMBER \
                    -m pytest -q
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION |
                    docker login --username AWS --password-stdin $REGISTRY

                    docker push $IMAGE:$BUILD_NUMBER
                    docker push $IMAGE:latest
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh 'bash scripts/deploy_remote.sh'
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f'
        }
    }
}
