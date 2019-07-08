#!/usr/bin/env python
#
# This file is part of alert_stream.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Generates batches of alerts coming from a CCD given template alert
content.
"""

import argparse
import asyncio
import glob
import itertools
import time
from lsst.alert.stream import alertProducer
from lsst.alert.packet import retrieve_alerts

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
        start_time = time.time()
        print('visit:', f[15:20], '\ttime:', start_time)
        # Load alert contents
        with open(f, mode='rb') as file_data:
            # TODO replace Avro files with visits having better S/N cut
            # for now, limit to first 10,000 alerts (current have ~70,000)
            schema, alert_packets = retrieve_alerts(file_data)
        ALERTS_TO_SEND = 10000
        for alert_count, record in enumerate(alert_packets):
            if alert_count < ALERTS_TO_SEND:
                streamProducer.send(schema, record)
            else:
                break
        streamProducer.flush()
        print(f"Sent {alert_count} alerts in {time.time() - start_time}s.")

    # Schedule visits to be send every `interval` seconds.
    loop = asyncio.get_event_loop()
    interval = 39  # Seconds between visits
    for delay, filename in zip(itertools.count(0, interval), files):
        loop.call_later(delay, send_visit, filename)

    # Shut down the event loop after the last visit has been sent.
    loop.call_later(delay, loop.stop)
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
