#!/bin/bash

docker network create --driver overlay alert_stream_default

docker service create \
        --name zookeeper \
        --network alert_stream_default \
        --constraint node.role==manager \
        -p 32181 \
        -e ZOOKEEPER_CLIENT_PORT=32181 \
        -e ZOOKEEPER_TICK_TIME=2000 \
        confluentinc/cp-zookeeper:4.1.1

docker service create \
        --name kafka \
        --network alert_stream_default \
        --constraint node.role==manager \
        -p 9092 \
        -e KAFKA_BROKER_ID=1 \
        -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:32181 \
        -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 \
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
        -e KAFKA_HEAP_OPTS="-Xmx8g -Xms8g" \
        -e KAFKA_JVM_PERFORMANCE_OPTS="-XX:MetaspaceSize=96m -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:G1HeapRegionSize=16M -XX:MinMetaspaceFreeRatio=50 -XX:MaxMetaspaceFreeRatio=80" \
        confluentinc/cp-kafka:4.1.1

