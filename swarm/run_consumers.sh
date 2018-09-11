#!/bin/bash

# $1 = node id
# $2 = broker url:port
# $3 = starting consumer stream
# $4 = ending consumer stream

#for i in `seq  -f "%03g" $3 $4`
for i in `seq  $3 $4`
    do
       filnum=$(printf "%03g" $i)

	docker service create \
        --name monitor$filnum \
        --network alert_stream_default \
        --constraint node.id==$1 \
	--endpoint-mode=dnsrr \
        -e PYTHONUNBUFFERED=0 \
        alert_stream python bin/monitorStream.py $2 Filter$filnum
    done
