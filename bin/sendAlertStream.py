#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert
content.
"""

from __future__ import print_function
import argparse
from lsst.alert.stream import alertProducer, avroUtils


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic stream to push to.')
    parser.add_argument('avrofile', type=str,
                        help='File from which to read alerts.')
    avrogroup = parser.add_mutually_exclusive_group()
    avrogroup.add_argument('--encode', dest='avroFlag', action='store_true',
                           help='Encode to Avro format. (default)')
    avrogroup.add_argument('--encode-off', dest='avroFlag',
                           action='store_false',
                           help='Do not encode to Avro format.')
    parser.set_defaults(avroFlag=True)

    args = parser.parse_args()

    # Configure Avro writer schema and data
    schema_files = ["../sample-avro-alert/schema/diasource.avsc",
                    "../sample-avro-alert/schema/diaobject.avsc",
                    "../sample-avro-alert/schema/ssobject.avsc",
                    "../sample-avro-alert/schema/cutout.avsc",
                    "../sample-avro-alert/schema/alert.avsc"]

    # Configure producer connection to Kafka broker
    conf = {'bootstrap.servers': 'kafka:9092'}
    streamProducer = alertProducer.AlertProducer(
                        args.topic, schema_files, **conf)

    # Scan for avro files
    root = "./data"
    afile = "/".join((root, args.avrofile))
    print('visit:', args.avrofile[7:12])
    # Load template alert contents
    with open(afile, mode='rb') as file_data:
        data = avroUtils.readSchemaData(file_data)
        for record in data:
            streamProducer.send(record, encode=True)


if __name__ == "__main__":
    main()
