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

import struct
from io import BytesIO

import confluent_kafka

from lsst.alert.packet import SchemaRegistry

__all__ = ['AlertProducer']


class AlertProducer(object):
    """Alert stream producer with Kafka.

    Parameters
    ----------
    topic : `str`
        The name of the topic stream for writing.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Producer().
    """

    def __init__(self, topic, **kwargs):
        self.producer = confluent_kafka.Producer(**kwargs)
        self.topic = topic

    def send(self, schema, data):
        """Sends a message to Kafka stream.

        The message is encoded following the `Confluent Wire Format`_. Thus:

        Byte 0:     ``0``.
        Byte 1-4:   A 4-byte schema ID.
        Byte 5-...: The packet data, Avro encoded following `schema`.

        .. _Confluent Wire Format: https://docs.confluent.io/current/schema-registry/docs/serializer-formatter.html#wire-format

        Parameters
        ----------
        schema : `lsst.alert.packet.Schema`
            The Avro schema for encoding data. Although one is not required to
            construct the producer, you can't begin sending data until one has
            been supplied.
        data : `dict`
            Message content. Must comply with the `schema`.
        """
        outgoing_bytes = BytesIO()
        outgoing_bytes.write(struct.pack("!b", 0))
        outgoing_bytes.write(struct.pack("!I", SchemaRegistry.calculate_id(schema)))
        outgoing_bytes.write(schema.serialize(data))
        self.producer.produce(self.topic, outgoing_bytes.getvalue())

    def flush(self):
        return self.producer.flush()
