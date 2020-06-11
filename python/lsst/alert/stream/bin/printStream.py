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

"""Consumes stream for printing all messages to the console.

Note that consumers with the same group ID share a stream.
To run multiple consumers each printing all messages,
each consumer needs a different group.
"""

import argparse
import sys
import os
from lsst.alert.stream import alertConsumer


def msg_text(message):
    """Remove postage stamp cutouts from an alert message.
    """
    message_text = {k: message[k] for k in message
                    if k not in ['cutoutDifference', 'cutoutTemplate']}
    return message_text


def write_stamp_file(stamp_dict, output_dir):
    """Given a stamp dict that follows the cutout schema,
       write data to a file in a given directory.
    """
    try:
        filename = stamp_dict['fileName']
        try:
            os.makedirs(output_dir)
        except OSError:
            pass
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'wb') as f:
            f.write(stamp_dict['stampData'])
    except TypeError:
        sys.stderr.write('%% Cannot get stamp\n')
    return


def alert_filter(alert, stampdir=None):
    """Filter to apply to each alert.
       See schemas here: https://github.com/lsst-dm/sample-avro-alert
    """
    data = msg_text(alert)
    if data:  # Write your condition statement here
        print(data)  # Print main alert data to screen
        if stampdir:  # Collect all postage stamps **There are no stamps**
            write_stamp_file(
                alert.get('cutoutDifference'), stampdir)
            write_stamp_file(
                alert.get('cutoutTemplate'), stampdir)
    return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('broker', type=str,
                        help='Hostname or IP and port of Kafka broker.')
    parser.add_argument('topic', type=str,
                        help='Name of Kafka topic to listen to.')
    parser.add_argument('interval', type=int,
                        help='Print every Nth alert.')
    parser.add_argument('--group', type=str,
                        help='Globally unique name of the consumer group. '
                        'Consumers in the same group will share messages '
                        '(i.e., only one consumer will receive a message, '
                        'as in a queue). Default is value of $HOSTNAME.')
    parser.add_argument('--stampDir', type=str,
                        help='Output directory for writing postage stamp'
                        'cutout files. **THERE ARE NO STAMPS RIGHT NOW.**')

    args = parser.parse_args()

    # Configure consumer connection to Kafka broker
    conf = {'bootstrap.servers': args.broker,
            'default.topic.config': {'auto.offset.reset': 'smallest'}}
    if args.group:
        conf['group.id'] = args.group
    else:
        conf['group.id'] = os.environ['HOSTNAME']

    # Start consumer and print alert stream
    with alertConsumer.AlertConsumer(args.topic, **conf) as streamReader:
        msg_count = 0
        while True:
            try:
                schema, msg = streamReader.poll()

                if msg is None:
                    continue
                else:
                    msg_count += 1
                    if msg_count % args.interval == 0:
                        # Apply filter to each alert
                        alert_filter(msg, args.stampDir)

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
