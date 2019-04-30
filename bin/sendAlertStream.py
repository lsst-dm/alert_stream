#!/usr/bin/env python

"""Generates batches of alerts coming from a CCD given template alert
content.
"""

from __future__ import print_function
import argparse
import glob
import time
import asyncio
from lsst.alert.stream import alertProducer
from lsst.alert.packet import retrieve_alerts


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
    yield from asyncio.sleep(wait_sec)
    return function(*args)


@asyncio.coroutine
def schedule_delays(eventloop, function, argslist, interval=39):
    """Schedule delayed calls of functions at a repeating interval.
    Parameters
    ----------
    eventloop
        Event loop returned by asyncio.get_event_loop().
    function
        Function to be scheduled.
    argslist
        List of inputs for function to loop over.
    interval
        Time in seconds between calls.
    """
    counter = 1
    for arg in argslist:
        wait_time = interval - (time.time() % interval)
        yield from asyncio.ensure_future(delay(wait_time, function, arg))
        print('visits finished: {} \t time: {}'.format(counter, time.time()))
        counter += 1
    eventloop.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('broker', type=str,
                        help='Hostname or IP and port of Kafka broker.')
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic stream to push to.')
    args = parser.parse_args()

    # Configure producer connection to Kafka broker
    conf = {'bootstrap.servers': args.broker}
    streamProducer = alertProducer.AlertProducer(args.topic, **conf)

    # Scan for avro files
    root = "./data"
    files = [f for f in glob.glob("/".join([root, "*.avro"]))]
    files.sort()

    def send_visit(f):
        print('visit:', f[15:20], '\ttime:', time.time())
        # Load alert contents
        with open(f, mode='rb') as file_data:
            # TODO replace Avro files with visits having better S/N cut
            # for now, limit to first 10,000 alerts (current have ~70,000)
            schema, alert_packets = retrieve_alerts(file_data)
            alert_count = 0
            for record in alert_packets:
                if alert_count < 10000:
                    streamProducer.send(schema, record)
                    alert_count += 1
                else:
                    break
        streamProducer.flush()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(schedule_delays(loop, send_visit, files))
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
