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

"""Consumes alert stream and prints all messages to the console.

Proof of concept using asyncio/aiokafka.
"""

import asyncio
import platform
import struct

from typing import Tuple

from aiokafka import AIOKafkaConsumer

from lsst.alert.packet import Schema
from lsst.alert.packet import SchemaRegistry

class Decoder(object):
    """Avro alert packet deserializer.

    Paramters
    ---------
    schema
        If supplied, always uses this schema to decode events. Otherwise, an
        appropriate schema is retrieved from the registry.
    """
    def __init__(self, schema: Schema=None) -> None:
        self.schema = schema
        self.schema_registry = SchemaRegistry.from_filesystem()

    def __call__(self, raw_bytes: bytes) -> Tuple[Schema, dict]:
        """Decode Avro-serialized raw bytes.

        Parameters
        ----------
        raw_bytes
            Data to be decoded. Assumed to be in Confluent wire format.

        Returns
        -------
        schema
            The schema used to decode the message.
        message
            The decoded message.
        """
        schema_hash = struct.unpack("!I", raw_bytes[1:5])[0]
        schema = (self.schema if self.schema is not None else
                  self.schema_registry.get_by_id(schema_hash))
        return schema, schema.deserialize(raw_bytes[5:])

async def consume() -> None:
    consumer = AIOKafkaConsumer(
        'my-stream',
        loop=loop,
        bootstrap_servers='localhost:29092',
        value_deserializer=Decoder(),
        group_id=platform.node())
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(consume())
