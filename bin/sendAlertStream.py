#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert content.
"""

from __future__ import print_function
import time
import argparse
import json
from lsst.alert.stream import alertProducer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic stream to push to.')
    parser.add_argument('alertnum', type=int,
                        help='Number of alerts to send.')

    args = parser.parse_args()

    # Configure producer connection to Kafka broker
    conf = {'bootstrap.servers': 'localhost:9092'}

    # Configure Avro writer schema and data
    schema_files = ["../sample-avro-alert/schema/diasource.avsc",
                    "../sample-avro-alert/schema/diaobject.avsc",
                    "../sample-avro-alert/schema/ssobject.avsc",
                    "../sample-avro-alert/schema/cutout.avsc",
                    "../sample-avro-alert/schema/alert.avsc"]
    json_path = "../sample-avro-alert/data/alert.json"

    # Load template alert contents
    with open(json_path) as file_text:
        json_data = json.load(file_text)

    # Configure Kafka producer with topic and schema
    streamProducer = alertProducer.AlertProducer(args.topic, schema_files, **conf)

    start_time = time.time()
    print("start time:{:.3f}".format(start_time))

    # Send alerts to producer
    for i in range(args.alertnum):
        streamProducer.send(json_data, encode=True)
    streamProducer.flush()
    finish_time = time.time()

    print("finish time:{:.3f}".format(finish_time))
    print("delta time:{:.3f}".format(finish_time - start_time))


if __name__ == "__main__":
    main()
