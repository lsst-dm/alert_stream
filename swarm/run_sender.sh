#!/bin/bash

# $1 = node

docker service create \
              --name sender \
              --network alert_stream_default \
              --constraint node.id==$1 \
	      --endpoint-mode=dnsrr \
              -e PYTHONUNBUFFERED=0 \
              alert_stream python bin/sendAlertStream.py kafka:9092 full-stream
