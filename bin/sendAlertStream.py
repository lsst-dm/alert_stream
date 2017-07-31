#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert
content.
"""

from __future__ import print_function
import time
import argparse
import json
import os.path
import asyncio
from glob import glob
from lsst.alert.stream import alertProducer
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter


def load_stamp(file_path):
    """Load a cutout postage stamp file to include in alert.
    """
    _, fileoutname = os.path.split(file_path)
    with open(file_path, mode='rb') as f:
        cutout_data = f.read()
        cutout_dict = {"fileName": fileoutname, "stampData": cutout_data}
    return cutout_dict


@asyncio.coroutine
def delay(wait_sec, function, *args):
    """Sleep for a given time before calling a function.

    Parameters
    ----------
    wait_sec
        Time in seconds to sleep before calling `function`.
    function
        Function to return after sleeping.
    """
    print('delay starting: {}'.format(time.time()))
    yield from asyncio.sleep(wait_sec)
    print('delay done sleeping: {}'.format(time.time()))
    return function(*args)
    print('delay finished: {}'.format(time.time()))


@asyncio.coroutine
def schedule_delays(eventloop, function, maxcounts, *args, interval=39):
    """Schedule delayed calls of a function at a repeating interval.

    Parameters
    ----------
    eventloop
        Event loop returned by asyncio.get_event_loop().
    function
        Function to be scheduled.
    maxcounts
        Maximum number of times `function` should be called.
    interval
        Time in seconds between calls.
    """
    counter = 0
    while counter < maxcounts:
        wait_time = interval - (time.time() % interval)
        yield from asyncio.ensure_future(delay(wait_time, function, *args))
        counter += 1
        print('batches finished: {}'.format(counter))
    else:
        eventloop.stop()


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
#    avrogroup = parser.add_mutually_exclusive_group()
#    avrogroup.add_argument('--encode', dest='avroFlag', action='store_true',
#                           help='Encode to Avro format. (default)')
#    avrogroup.add_argument('--encode-off', dest='avroFlag',
#                           action='store_false',
#                           help='Do not encode to Avro format.')
    parser.add_argument('--repeat', action='store_true',
                        help='Send alert batches repeating every 39th second.'
                        ' Default of 2215 batches (~24 hours).')
    parser.add_argument('--max-repeats', type=int, dest='batchnum',
                        help='Override default number of batches to send.')
    parser.set_defaults(stamps=True, avroFlag=True, batchnum=2215)

    args = parser.parse_args()

    # Configure producer connection to Kafka broker
    conf = {'bootstrap.servers': 'kafka:9092'}

    # Configure Avro writer schema and data
    schema_files = ["../ztf-avro-alert/schema/cutout.avsc",
                    "../ztf-avro-alert/schema/candidate.avsc",
                    "../ztf-avro-alert/schema/prv_candidate.avsc",
                    "../ztf-avro-alert/schema/alert.avsc"]
    #json_path = "../sample-avro-alert/data/alert.json"
    #cutoutdiff_path = "../sample-avro-alert/examples/stamp-676.fits"
    #cutouttemp_path = "../sample-avro-alert/examples/stamp-677.fits"

    avro_path = '../sample_v1.1_alerts/'

    avro_files = glob(avro_path + 
                      'ztf-realtime-04/rc34/20160820/sciprod/*/*/*.avro')
    n_files = len(avro_files)

    # Configure Kafka producer with topic and schema
    streamProducer = alertProducer.AlertProducer(
                        args.topic, schema_files, **conf)

    def read_avro_file(filename):
        with open(filename,'rb') as f:
            #yield f.read()
            freader = DataFileReader(f,DatumReader())
            for datum in freader:
                yield datum

    def load_avro_packets(list_of_files):
        for filename in list_of_files:
            yield from read_avro_file(filename)

    packet_gen = load_avro_packets(avro_files)

    def send_batch(packet_gen):
        start_time = time.time()
        print('batch start time:{:.3f}'.format(start_time))
        for i in range(args.alertnum):
            try:
                streamProducer.send(next(packet_gen), encode=False)
            except StopIteration:
                # reinitialize 
                packet_gen = load_avro_packets(avro_files)
        streamProducer.flush()
        finish_time = time.time()
        print('batch finish time:{:.3f}'.format(finish_time))
        print('batch delta time:{:.3f}'.format(finish_time - start_time))

    # Send alerts to producer
    print('start: {}'.format(time.time()))
    if args.repeat:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(schedule_delays(loop, send_batch, args.batchnum, packet_gen))
        loop.run_forever()
        loop.close()
    else:
        send_batch(packet_gen)
    print('finish: {}'.format(time.time()))


if __name__ == "__main__":
    main()
