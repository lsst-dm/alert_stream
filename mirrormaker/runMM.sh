#!/usr/bin/env bash

# default script for whitelisting everything
# requires config files below
/usr/bin/kafka-mirror-maker --consumer.config /home/mm/mm_consumer.properties --producer.config /home/mm/mm_producer.properties --whitelist=".*"

