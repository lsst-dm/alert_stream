#!/usr/bin/env python

"""Consumes stream for monitoring.

Note that consumers with the same group ID share a stream.
To run multiple consumers, each consumer needs a different group.
"""

from __future__ import print_function
import argparse
from lsst.alert.stream import alertConsumer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', metavar='topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('group', metavar='consumerId', type=str,
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

    # Start consumer and monitor alert stream
    streamListener = alertConsumer.AlertConsumer(topic, **conf)
    streamListener.watchBatches()

if __name__ == "__main__":
    main()
