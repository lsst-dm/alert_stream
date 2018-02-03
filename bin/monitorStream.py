#!/usr/bin/env python

"""Consumes stream for monitoring.

Note that consumers with the same group ID share a stream.
To run multiple consumers, each consumer needs a different group.
"""

from __future__ import print_function
import argparse
import os
import sys
from lsst.alert.stream import alertConsumer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('--group', type=str,
                        help='Globally unique name of the consumer group. '
                        'Consumers in the same group will share messages '
                        '(i.e., only one consumer will receive a message, '
                        'as in a queue). Default is value of $HOSTNAME.')
    args = parser.parse_args()

    # Configure consumer connection to Kafka broker
    conf = {'bootstrap.servers': 'epyc.astro.washington.edu:9092',
            'default.topic.config': {'auto.offset.reset': 'smallest'}}
    if args.group:
        conf['group.id'] = args.group
    else:
        conf['group.id'] = os.environ['HOSTNAME']

    # Start consumer and monitor alert stream
    streamWatcher = alertConsumer.AlertConsumer(args.topic, **conf)

    while True:
        try:
            msg = streamWatcher.poll(decode=False, verbose=False)

            if msg is None:
                continue
            else:
                print(msg)

        except alertConsumer.EopError as e:
            # Write when reaching end of partition
            sys.stderr.write(e.message)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
            sys.exit()


if __name__ == "__main__":
    main()
