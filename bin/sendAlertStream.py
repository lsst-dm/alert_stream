#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert content.
"""

from __future__ import print_function
import time
import argparse
import json
import os.path
from lsst.alert.stream import alertProducer


def load_stamp(file_path):
    """Load a cutout postage stamp file to include in alert.
    """
    _, fileoutname = os.path.split(file_path)
    with open(file_path, mode='rb') as f:
        cutout_data = f.read()
        cutout_dict = {"fileName": fileoutname, "stampData": cutout_data}
    return cutout_dict


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic stream to push to.')
    parser.add_argument('alertnum', type=int,
                        help='Number of alerts to send.')
    stampgroup = parser.add_mutually_exclusive_group()
    stampgroup.add_argument('--stamps', dest='stamps', action='store_true',
                            help='Send postage stamp cutouts. (default)')
    stampgroup.add_argument('--no-stamps', dest='stamps', action='store_false',
                            help='Do not send postage stamp cutouts.')
    avrogroup = parser.add_mutually_exclusive_group()
    avrogroup.add_argument('--encode', dest='avroFlag', action='store_true',
                           help='Encode to Avro format. (default)')
    avrogroup.add_argument('--encode-off', dest='avroFlag', action='store_false',
                           help='Do not encode to Avro format.')
    parser.set_defaults(stamps=True, avroFlag=True)

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
    cutoutdiff_path = "../sample-avro-alert/examples/stamp-676.fits"
    cutouttemp_path = "../sample-avro-alert/examples/stamp-677.fits"

    # Load template alert contents
    with open(json_path) as file_text:
        json_data = json.load(file_text)

    # Add postage stamp cutouts
    if args.stamps:
        json_data['cutoutDifference'] = load_stamp(cutoutdiff_path)
        json_data['cutoutTemplate'] = load_stamp(cutouttemp_path)

    # Configure Kafka producer with topic and schema
    streamProducer = alertProducer.AlertProducer(args.topic, schema_files, **conf)

    start_time = time.time()
    print("start time:{:.3f}".format(start_time))

    # Send alerts to producer
    for i in range(args.alertnum):
        streamProducer.send(json_data, encode=args.avroFlag)
    streamProducer.flush()
    finish_time = time.time()

    print("finish time:{:.3f}".format(finish_time))
    print("delta time:{:.3f}".format(finish_time - start_time))


if __name__ == "__main__":
    main()
