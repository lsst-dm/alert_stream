"""Utilities for talking to Kafka.
"""

from __future__ import print_function, absolute_import
import io
import sys
import time
from confluent_kafka import KafkaException, KafkaError
from . import avroUtils


__all__ = ['writeEopNotice', 'decodeMessage', 'writeAllReceipts', 'printAllMessages']


def writeEopNotice(msg):
    """Send end of partition notice to stderr when no messages left to consume.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    """
    if msg.error().code() == KafkaError._PARTITION_EOF:
        sys.stderr.write('topic:%s, partition:%d, status:end, offset:%d, key:%s, time:%.3f\n' %
                         (msg.topic(), msg.partition(), msg.offset(), str(msg.key()),  time.time()))
    elif msg.error():
        raise KafkaException(msg.error())
    return


def decodeMessage(msg, schema):
    """Decode Avro message according to a schema.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    schema : Avro schema
        The reader Avro schema for decoding message.

    Returns
    -------
    `dict`
        Decoded message.
    """
    message = msg.value()
    bytes_io = io.BytesIO(message)
    try:
        decoded_msg = avroUtils.readAvroData(bytes_io, schema)
    except AssertionError:
        # FIXME this exception is being raised but not sure if it matters yet
        pass
    return decoded_msg


def writeAllReceipts(msg):
    """Writes end of partition notice and receipts for all messages.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    """
    if msg.error():
        writeEopNotice(msg)
    else:
        # TODO use logging instead maybe
        sys.stderr.write('topic:%s, partition:%d, status:at, offset:%d, key:%s, time:%.3f\n' %
                         (msg.topic(), msg.partition(), msg.offset(), str(msg.key()), time.time()))


def printAllMessages(msg, schema):
    """Print decoded message stream to the console.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    schema : Avro schema
        The reader Avro schema for decoding message.
    """
    if msg.error():
        writeEopNotice(msg)
    else:
        decoded_msg = decodeMessage(msg, schema)
        print(decoded_msg)
        sys.stdout.flush()
