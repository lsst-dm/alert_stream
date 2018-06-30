# Deployment commands for running alert distribution
# and mini-broker system with Kubernetes
kubectl create -f zookeeper-service.yaml
kubectl create -f zookeeper-deployment.yaml
kubectl create -f kafka-deployment.yaml
kubectl create -f kafka-service.yaml
# For testing, you can run only consumer1 and filterer1 below
kubectl create -f consumer1-deployment.yaml
kubectl create -f consumer2-deployment.yaml
kubectl create -f consumer3-deployment.yaml
kubectl create -f consumer4-deployment.yaml
kubectl create -f consumer5-deployment.yaml
kubectl create -f consumer6-deployment.yaml
kubectl create -f consumer7-deployment.yaml
kubectl create -f consumer8-deployment.yaml
kubectl create -f consumer9-deployment.yaml
kubectl create -f consumer10-deployment.yaml
kubectl create -f filterer1-deployment.yaml
kubectl create -f filterer2-deployment.yaml
kubectl create -f filterer3-deployment.yaml
kubectl create -f filterer4-deployment.yaml
kubectl create -f filterer5-deployment.yaml
# To use the sims data included in the Docker image, run:
kubectl create -f sender-deployment.yaml
# Alternatively, for 1 full night of sims data,
# night 15 of the minion_1016 OpSim run, run:
kubectl create -f alert-data-persistentvolumeclaim.yaml
kubectl create -f sender-volume-deployment.yaml
