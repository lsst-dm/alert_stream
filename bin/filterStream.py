#!/usr/bin/env python

"""Template alert stream filter.

Runs a set of filters on a single instance of a stream in parallel.
"""

from __future__ import print_function
import argparse
import sys
import os
import inspect
from multiprocessing import Pool
from collections import defaultdict

from lsst.alert.stream import alertConsumer, alertProducer
from lsst.alert.stream import filterBase
from lsst.alert.stream import filters as fl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('firstFilter', type=int,
                        help='Number of the first filter in range '
                        '(1-100) to deploy.')
    parser.add_argument('lastFilter', type=int,
                        help='Number of the last filter in range '
                        '(1-100) to deploy.')
    parser.add_argument('--group', type=str,
                        help='Globally unique name of the consumer group. '
                        'Consumers in the same group will share messages '
                        '(i.e., only one consumer will receive a message, '
                        'as in a queue). Default is value of $HOSTNAME.')
    avrogroup = parser.add_mutually_exclusive_group()
    avrogroup.add_argument('--decode', dest='avroFlag', action='store_true',
                           help='Decode from Avro format. (default)')
    avrogroup.add_argument('--decode-off', dest='avroFlag',
                           action='store_false',
                           help='Do not decode from Avro format.')
    parser.set_defaults(avroFlag=True)

    args = parser.parse_args()
    f1 = args.firstFilter
    f2 = args.lastFilter

    # Configure Avro reader schema
    schema_files = ["../sample-avro-alert/schema/diasource.avsc",
                    "../sample-avro-alert/schema/diaobject.avsc",
                    "../sample-avro-alert/schema/ssobject.avsc",
                    "../sample-avro-alert/schema/cutout.avsc",
                    "../sample-avro-alert/schema/alert.avsc"]

    # Configure consumer connection to Kafka broker
    cconf = {'bootstrap.servers': 'kafka:9092',
             'default.topic.config': {'auto.offset.reset': 'smallest'}}
    if args.group:
        cconf['group.id'] = args.group
    else:
        cconf['group.id'] = os.environ['HOSTNAME']

    pconf = {'bootstrap.servers': 'kafka:9092'}

    # Get all filter classes from filters module
    filter_list = [c[1] for c in
                   inspect.getmembers(fl, inspect.isclass)[f1:f2+1]]

    # Name all output streams using filter class name
    topic_list = [x.__name__ for x in filter_list]

    def makeFilters(topic_list, filter_list):

        filters = []
        for t, f in zip(topic_list, filter_list):
            prod = alertProducer.AlertProducer(t, schema_files, **pconf)
            exp = filterBase.StreamExporter(prod)
            filter = f(t)
            filters.append((filter, exp, defaultdict(int)))
        # Remove top level base class
        return filters

    filters = makeFilters(topic_list, filter_list)  # list of classes

    # Start consumer and print alert stream
    with alertConsumer.AlertConsumer(args.topic, schema_files,
                                     **cconf) as streamReader:

        def init_worker(topics, schema_files, pconf):
            global exporters
            exporters = dict()
            for t in topics:
                prod = alertProducer.AlertProducer(t, schema_files, **pconf)
                exp = filterBase.StreamExporter(prod)
                exporters[t] = exp

        with Pool(10, initializer=init_worker,
                  initargs=(topic_list, schema_files, pconf)) as p:
            while True:
                try:
                    msg = streamReader.poll(decode=True)

                    if msg is None:
                        continue
                    else:
                        # Apply filters to each alert
                        for f, exp, counts in filters:
                            visit = f.getVisit(msg)
                            if counts[visit] < 20:
                                def make_cb(exp, msg, counts, visit):
                                    def cb(result):
                                        if result:
                                            counts[visit] += 1
                                            if counts[visit] <= 20:
                                                exp(msg)
                                    return cb
                            p.apply_async(f, args=(msg,),
                                          callback=make_cb(exp, msg,
                                                           counts, visit))

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
