   pipeline {
     agent any
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
               echo $P | podman login docker.io -u $U --password-stdin
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
             kubectl -n $NAMESPACE rollout status deployment/$DEPLOY --timeout=300s
           '''
         }
       }
     }
     post {
       failure { sh 'kubectl -n $NAMESPACE rollout undo deployment/$DEPLOY || true' }
     }
   }
