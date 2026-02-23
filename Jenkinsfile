pipeline {
    agent {
        label 'jenkins-agent2'
    }

    stages {
        stage('Pull Latest') {
            steps {
                sh 'cd ~/garminconnector && git pull'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'cd ~/garminconnector && docker compose build --no-cache garmin-report'
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
