#!/bin/bash

# $1 = node
# $2 = broker url:port
# $3 = starting filter num
# $4 = ending filter num

#for i in `seq  -f "%03g" $3 $4`
for i in `seq $3 $4`
    do
        filnum=$(printf "%03g" $i)
        num=$(echo $i | sed 's/^0*//')

        docker service create \
        --name filter$filnum \
        --network alert_stream_default \
        --constraint node.id==$1 \
        --endpoint-mode=dnsrr \
        -e PYTHONUNBUFFERED=0 \
        alert_stream python bin/filterStream.py $2 full-stream $num
    done
