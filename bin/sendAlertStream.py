#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert
content.
"""

from __future__ import print_function
import argparse
import glob
import time
from lsst.alert.stream import alertProducer, avroUtils


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic stream to push to.')
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
    root = "../data"
    files = [f for f in glob.glob("/".join([root, "*.avro"]))]
    for f in files:
        print('visit:', f[15:20], '\ttime:', time.time())
        # Load alert contents
        with open(f, mode='rb') as file_data:
            data = avroUtils.readSchemaData(file_data)
            # TODO replace Avro files with visits having better S/N cut
            # for now, limit to first 10,000 alerts (current have ~70,000)
            alert_count = 0
            for record in data:
                if alert_count < 10000:
                    streamProducer.send(record, encode=True)
                    alert_count += 1
                else:
                    break
            streamProducer.flush()


if __name__ == "__main__":
    main()
