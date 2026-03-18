pipeline {
    agent {
        label 'jenkins-agent'
    }

    stages {
        stage('Sync Host Repo') {
            steps {
                sh 'ssh -i /home/jenkins/.ssh/id_rsa -o StrictHostKeyChecking=no strider@192.168.1.199 "cd ~/garminconnector && git checkout -- . && git pull"'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker compose -p garminconnector build --no-cache garmin-report'
            }
        }
    }

    post {
        success {
            echo 'GarminConnector Docker image rebuilt successfully.'
        }
        failure {
            echo 'Build failed. Check logs.'
        }
    }
}
