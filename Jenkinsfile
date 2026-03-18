pipeline {
    agent {
        label 'jenkins-agent'
    }

    stages {
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
