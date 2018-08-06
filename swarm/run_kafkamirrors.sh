#!/bin/bash

# $1 - $N nodes

#for i in `seq -f "%02g" 1 "$#"`
for i in $(seq -w 01 "$#")

    do
        num=$(echo $i | sed 's/^0*//')
        kport=$((9092+$num))
        zooport=$((32181+$num))
        arg=${!i}

        docker service create \
        --name kafka$i \
        --network alert_stream_default \
        --constraint node.id==$arg \
        -p $kport \
        -e KAFKA_BROKER_ID=$num \
        -e KAFKA_ZOOKEEPER_CONNECT=zookeeper$i:$zooport \
        -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka$i:$kport \
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
        -e KAFKA_HEAP_OPTS="-Xmx8g -Xms8g" \
        -e KAFKA_JVM_PERFORMANCE_OPTS="-XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80" \
        confluentinc/cp-kafka:4.1.1

    done

