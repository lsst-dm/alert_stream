#!/bin/bash

# $1 - $N nodes

#for i in `seq -f "%02g" 1 "$#"`
for i in $(seq -w 01 "$#")

    do
        num=$(echo $i | sed 's/^0*//')
        zooport=$((32181+$num))
        arg=${!i}

        docker service create \
        --name zookeeper$i \
        --network alert_stream_default \
        --constraint node.id==$arg \
        -p $zooport \
        -e ZOOKEEPER_CLIENT_PORT=$zooport \
        -e ZOOKEEPER_TICK_TIME=2000 \
        confluentinc/cp-zookeeper:4.1.1

    done

