#!/usr/bin/env python

"""Consumes stream for printing all messages to the console.

Note that consumers with the same group ID share a stream.
To run multiple consumers each printing all messages, each consumer needs a different group.
"""

from __future__ import print_function
import argparse
from lsst.alert.stream import avroUtils
from lsst.alert.stream import alertConsumer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', metavar='topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('group', metavar='consumerGroupId', type=str,
                        help='Globally unique name of the consumer group. '
                        'Consumers in the same group will share messages '
                        '(i.e., only one consumer will receive a message, as in a queue).')
    args = parser.parse_args()
    topic = args.topic
    group = args.group

    # Configure consumer connection to Kafka broker
    conf = {'bootstrap.servers': 'localhost:9092',
            'group.id': group,
            'default.topic.config': {'auto.offset.reset': 'smallest'}}

    # Configure Avro reader schema
    schema_path = ["../sample-avro-alert/schema/diasource.avsc",
                   "../sample-avro-alert/schema/diaobject.avsc",
                   "../sample-avro-alert/schema/ssobject.avsc",
                   "../sample-avro-alert/schema/alert.avsc"]
    alert_schema = avroUtils.combineSchemas(schema_path)

    # Start consumer and print alert stream
    streamListener = alertConsumer.AlertConsumer(topic, **conf)
    streamListener.printAlertStream(alert_schema)

if __name__ == "__main__":
    main()
