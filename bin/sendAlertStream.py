#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert content.
"""

from __future__ import print_function
import argparse
import json
from confluent_kafka import Producer
from lsst.alert.stream import avroAlertGen
from lsst.alert.stream import avroUtils


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', metavar='topic', type=str,
                        help='Name of Kafka topic stream to push to.')
    parser.add_argument('ccd', metavar='ccdId', type=int,
                        help='CCD ID number.')
    parser.add_argument('alertnum', metavar='alertnum', type=int,
                        help='Number of alerts per CCD.')

    args = parser.parse_args()
    topic = args.topic
    ccdnum = args.ccd
    alertnum = args.alertnum

    # Set up producer connection to Kafka broker
    conf = {'bootstrap.servers': 'localhost:9092'}
    producer = Producer(**conf)

    # Configure Avro writer schema and data
    schema_path = ["../sample-avro-alert/schema/diasource.avsc",
                   "../sample-avro-alert/schema/diaobject.avsc",
                   "../sample-avro-alert/schema/ssobject.avsc",
                   "../sample-avro-alert/schema/alert.avsc"]
    alert_schema = avroUtils.combineSchemas(schema_path)
    json_path = "../sample-avro-alert/data/alert.json"

    # Load template alert contents
    with open(json_path) as file_text:
        json_data = json.load(file_text)

    # Generate and send alerts to Kafka producer
    alertGen = avroAlertGen.AvroAlertGen(json_data, alert_schema, ccdnum)
    alertGen.sendAlerts(producer, topic, alertnum)


if __name__ == "__main__":
    main()
