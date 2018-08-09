#!/bin/bash

# $1 - $N = nodes

#for i in `seq -f "%02g" 1 "$#"`
for i in `seq -w 01 "$#"`
    do 
       i=$(printf "%02d" $i)
       num=$(echo $i | sed 's/^0*//')
       zooport=$((32181+$num))
       kport=$((9092+$num))
       arg=${!i}

        docker service create \
        --name mirrormaker$i \
        --network alert_stream_default \
        --constraint node.id==$arg \
        -e KAFKA_ZOOKEEPER_CONNECT=zookeeper$i:$zooport \
        -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://mirrormaker$i:$kport \
        mtpatter/mirrormaker /usr/bin/kafka-mirror-maker --consumer.config /home/mm/mm_consumer$i.properties --producer.config /home/mm/mm_producer$i.properties --whitelist=".*"

    done
