#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert
content.
"""

from __future__ import print_function
import time
import argparse
import os
import glob
from lsst.alert.stream import alertProducer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic stream to push to.')
    parser.add_argument('startdate', type=int,
                        help='First date from which to read alerts.')
    parser.add_argument('pause', type=int,
                        help='Number of seconds to pause between visits.')


    args = parser.parse_args()

    # Configure producer connection to Kafka broker
    conf = {'bootstrap.servers': 'kafka:9092'}
    streamProducer = alertProducer.AlertProducer(
                        args.topic, **conf)

    # Scan for avro files
    root = "../data"
    subdirectories = [d for d in os.listdir(os.path.join(root)) if d >= str(args.startdate)]
    subdirectories.sort()
    for d in subdirectories:
        print('date:', d)
        points = [p for p in os.listdir(os.path.join(root, d))]
        points.sort()
        for p in points:
            visitdirs = [v for v in glob.glob("/".join((root, d, p, 'ccd*/*')))]
            uvisitquads = [os.path.basename(v) for v in visitdirs]
            visits = []
            for u in uvisitquads:
                visits.append("_".join(u.split("_")[0:4]))
            visits.sort()
            visits = set(visits)
            for v in visits:
                files = [f for f in glob.glob("/".join((root, d, p, "ccd*", "".join((v, "*/*")))))]
                print('visit:', v)
                for f in files:
                    # Load template alert contents
                    with open(f, mode='rb') as file_text:
                        data = file_text.read()
                        streamProducer.send(data, encode=False)
                time.sleep(args.pause)


if __name__ == "__main__":
    main()
