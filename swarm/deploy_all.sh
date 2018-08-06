#!/bin/bash

# deploy main hub constrained to manager node
./run_kafka.sh

# deploy zookeeper mirrors, one per node
./run_zoomirrors.sh $(cat filternodes.txt | xargs)

# deploy kafka mirrors, one per node
./run_kafkamirrors.sh $(cat filternodes.txt | xargs)

# deploy mirrormakers, one per node
./run_mirrormakers.sh $(cat filternodes.txt | xargs)

# deploy end consumers in groups of 20 per node
  i=01
  num=$(echo $i | sed 's/^0*//')
  port=$((9092+$num))
  start=1
  end=20

  while read n; do
      ./run_consumers.sh $n kafka$i:$port $start $end
      port=$(($port+1))
      start=$(($start+20))
      end=$(($end+20))
      i=$(printf '%02g' $(($i+1)) )
  done < consumernodes.txt

# deploy filters in groups of 20 per node
  i=01
  num=$(echo $i | sed 's/^0*//')
  port=$((9092+$num))
  start=1
  end=20

  while read n; do
      ./run_filters.sh $n kafka$i:$port $start $end
      port=$(($port+1))
      start=$(($start+20))
      end=$(($end+20))
      i=$(printf '%02g' $(($i+1)) )
  done < filternodes.txt

# deploy sender
  while read n; do
    ./run_sender.sh $n
  done < sendernodes.txt
