#!/usr/bin/env python

"""Alert stream filter deployer.
"""

from __future__ import print_function
import argparse
import sys
import os
import inspect
from lsst.alert.stream import alertConsumer, alertProducer
from lsst.alert.stream import filterBase
from lsst.alert.stream import filters
from lsst.alert.packet import SchemaRegistry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('broker', type=str,
                        help='Hostname or IP and port of Kafka broker.')
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('filterNum', type=int,
                        help='Number of the filter in range '
                        '(1-100) to deploy.')
    parser.add_argument('--group', type=str,
                        help='Globally unique name of the consumer group. '
                        'Consumers in the same group will share messages '
                        '(i.e., only one consumer will receive a message, '
                        'as in a queue). Default is value of $HOSTNAME.')

    args = parser.parse_args()
    fnum = args.filterNum

    # Configure consumer connection to Kafka broker
    cconf = {'bootstrap.servers': args.broker,
             'default.topic.config': {'auto.offset.reset': 'smallest'}}
    if args.group:
        cconf['group.id'] = args.group
    else:
        cconf['group.id'] = os.environ['HOSTNAME']

    pconf = {'bootstrap.servers': args.broker}

    # Choose filter class to deploy from filters module
    filter_class = inspect.getmembers(filters, inspect.isclass)[fnum][1]

    # Name output stream using filter class name
    topic_name = filter_class.__name__

    prod = alertProducer.AlertProducer(topic_name, **pconf)
    exp = filterBase.StreamExporter(prod)
    apply_filter = filter_class(exp)

    # Start consumer and print alert stream
    with alertConsumer.AlertConsumer(args.topic, **cconf) as streamReader:

        while True:
            try:
                schema, msg = streamReader.poll()

                if msg is None:
                    continue
                else:
                    # Apply filter to each alert
                    apply_filter(schema, msg)

            except alertConsumer.EopError as e:
                # Write when reaching end of partition
                sys.stderr.write(e.message)
            except IndexError:
                sys.stderr.write('%% Data cannot be decoded\n')
            except UnicodeDecodeError:
                sys.stderr.write('%% Unexpected data format received\n')
            except KeyboardInterrupt:
                sys.stderr.write('%% Aborted by user\n')
                sys.exit()


if __name__ == "__main__":
    main()
