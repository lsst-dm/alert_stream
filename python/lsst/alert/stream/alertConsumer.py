from __future__ import print_function
import io
import sys
import time
import confluent_kafka
from . import avroUtils


__all__ = ['AlertConsumer']


def _writeEopNotice(msg):
    """Send end of partition notice to stderr when no messages left to consume.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    """
    if msg.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
        sys.stderr.write('topic:%s, partition:%d, status:end, offset:%d, key:%s, time:%.3f\n' %
                         (msg.topic(), msg.partition(), msg.offset(), str(msg.key()),  time.time()))
    elif msg.error():
        raise confluent_kafka.KafkaException(msg.error())
    return


def _decodeMessage(msg, schema):
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
        decoded_msg = None
        pass
    return decoded_msg


class AlertConsumer(object):
    """Creates an alert stream Kafka consumer for a given topic.

    Parameters
    ----------
    topic : `str`
        Name of the topic to subscribe to.
    schema_files : Avro schema files
        The reader Avro schema files for decoding data. Optional.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Consumer().
    """

    def __init__(self, topic, schema_files=None, **kwargs):
        self.consumer = confluent_kafka.Consumer(**kwargs)
        self.consumer.subscribe([topic])
        if schema_files is not None:
            self.alert_schema = avroUtils.combineSchemas(schema_files)

    def poll(self, decode=False, verbose=True):
        """Polls Kafka broker to consume topic.

        Parameters
        ----------
        decode : `boolean`
            If True, decodes data from Avro format.
        verbose: `boolean`
            If True, returns every message. If False, returns only end of partition messages.
        """
        if decode is False:
            msg = self.consumer.poll()

            if msg.error():
                return _writeEopNotice(msg)
            else:
                if verbose is True:
                    return msg.value()
                else:
                    pass

        else:
            try:
                msg = self.consumer.poll()

                if msg.error():
                    return _writeEopNotice(msg)
                else:
                    if verbose is True:
                        return _decodeMessage(msg, self.alert_schema)
                    else:
                        pass

            except IndexError:
                sys.stderr.write('%% Data cannot be decoded.\n')
                pass
