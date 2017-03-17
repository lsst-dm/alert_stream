#!/bin/bash

NODES=3


## Create multiple hosts
for N in $(seq 1 $NODES)
do
docker-machine create --driver virtualbox node$N
done


## Set up swarm
### node1 as manager and others as workers
SWARM_ADDR=$(docker-machine ip node1)

docker-machine ssh node1 docker swarm init --advertise-addr $SWARM_ADDR

SWARM_TOKEN=$(docker-machine ssh node1 docker swarm join-token -q worker)

for N in $(seq 2 $NODES)
do
docker-machine ssh node$N docker swarm join --token $SWARM_TOKEN $SWARM_ADDR:2377
done


## Set up hosts
for N in $(seq 1 $NODES)
do
docker-machine ssh node$N 'git clone https://github.com/lsst-dm/alert_stream.git && cd alert_stream \
 && docker build -t "alert_stream" .'
done
