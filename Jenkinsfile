pipeline {
  agent { label 'vinod' }
  triggers { pollSCM('H/2 * * * *') }
  options {
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
  }
  environment {
    IMAGE     = "docker.io/umarfd123/help-desk"
    TAG       = "${env.BUILD_NUMBER}"
    NAMESPACE = "help-desk"
    DEPLOY    = "help-desk"
    CONTAINER = "app"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Build Image') {
      steps { sh 'podman build -t $IMAGE:$TAG -t $IMAGE:latest .' }
    }
    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
            usernameVariable: 'U', passwordVariable: 'P')]) {
          sh '''
            printf '%s' "$P" | podman login docker.io -u "$U" --password-stdin
            podman push $IMAGE:$TAG
            podman push $IMAGE:latest
          '''
        }
      }
    }
    stage('Deploy to K8s') {
      steps {
        sh '''
          kubectl -n $NAMESPACE set image deployment/$DEPLOY $CONTAINER=$IMAGE:$TAG
          if ! kubectl -n $NAMESPACE rollout status deployment/$DEPLOY --timeout=600s; then
            kubectl -n $NAMESPACE rollout undo deployment/$DEPLOY
            exit 1
          fi
        '''
      }
    }
  }
}
