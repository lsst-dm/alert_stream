from __future__ import print_function
import io
import time
import confluent_kafka
from ast import literal_eval
from . import avroUtils


__all__ = ['EopError', 'AlertConsumer']


class AlertError(Exception):
    """Base class for exceptions in this module.
    """
    pass


class EopError(AlertError):
    """Exception raised when reaching end of partition.

    Parameters
    ----------
    msg : Kafka message
        The Kafka message result from consumer.poll().
    """
    def __init__(self, msg):
        message = 'topic:%s, partition:%d, status:end, ' \
                  'offset:%d, key:%s, time:%.3f\n' \
                  % (msg.topic(), msg.partition(),
                     msg.offset(), str(msg.key()), time.time())
        self.message = message

    def __str__(self):
        return self.message


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
            If True, returns every message. If False, only raises EopError.
        """
        msg = self.consumer.poll()

        if msg.error():
            raise EopError(msg)
        else:
            if verbose is True:
                if decode is True:
                    return self.decodeMessage(msg)
                else:
                    ast_msg = literal_eval(str(msg.value(), encoding='utf-8'))
                    return ast_msg
        return

    def decodeMessage(self, msg):
        """Decode Avro message according to a schema.

        Parameters
        ----------
        msg : Kafka message
            The Kafka message result from consumer.poll().

        Returns
        -------
        `dict`
            Decoded message.
        """
        message = msg.value()
        bytes_io = io.BytesIO(message)
        try:
            decoded_msg = avroUtils.readAvroData(bytes_io, self.alert_schema)
        except AssertionError:
            # FIXME this exception is raised but not sure if it matters yet
            decoded_msg = None
        return decoded_msg
