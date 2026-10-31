pipeline {
    agent any

    environment {
        IMAGE_NAME = 'python-crud-api'
        CONTAINER_NAME = 'production-api-container'
        VOLUME_NAME = 'production-api-data'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Syntax Check') {
            steps {
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t python-crud-api:${BUILD_NUMBER} .'
                sh 'docker tag python-crud-api:${BUILD_NUMBER} python-crud-api:latest'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker volume create ${VOLUME_NAME}
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 5000:5000 \
                        -v ${VOLUME_NAME}:/var/lib/backend_data \
                        python-crud-api:latest
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    for i in $(seq 1 10); do
                        if curl -fsS http://localhost:5000/health; then
                            echo "API is healthy"
                            exit 0
                        fi
                        sleep 3
                    done

                    echo "Health check failed"
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }
    }
}