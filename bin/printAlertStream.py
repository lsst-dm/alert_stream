#!/usr/bin/env python

"""Consumes stream for printing all messages to the console.

Note that consumers with the same group ID share a stream.
To run multiple consumers each printing all messages, each consumer needs a different group.
"""

from __future__ import print_function
import argparse
import sys
from lsst.alert.stream import alertConsumer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('group', type=str,
                        help='Globally unique name of the consumer group. '
                        'Consumers in the same group will share messages '
                        '(i.e., only one consumer will receive a message, as in a queue).')
    args = parser.parse_args()

    # Configure consumer connection to Kafka broker
    conf = {'bootstrap.servers': 'localhost:9092',
            'group.id': args.group,
            'default.topic.config': {'auto.offset.reset': 'smallest'}}

    # Configure Avro reader schema
    schema_files = ["../sample-avro-alert/schema/diasource.avsc",
                    "../sample-avro-alert/schema/diaobject.avsc",
                    "../sample-avro-alert/schema/ssobject.avsc",
                    "../sample-avro-alert/schema/alert.avsc"]

    # Start consumer and print alert stream
    streamReader = alertConsumer.AlertConsumer(args.topic, schema_files, **conf)

    while True:
        try:
            msg = streamReader.poll(decode=True)

            if msg is None:
                continue
            else:
                print(msg)

        except alertConsumer.EopError as e:
            # Write when reaching end of partition
            sys.stderr.write(e.message)
        except IndexError:
            sys.stderr.write('%% Data cannot be decoded\n')
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
            sys.exit()


if __name__ == "__main__":
    main()
