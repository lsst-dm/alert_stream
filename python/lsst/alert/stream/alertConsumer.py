import struct
import time
import confluent_kafka

from lsst.alert.packet import SchemaRegistry

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
    schema : `lsst.alert.packet.Schema`, optional
        If provided, this schema is always used to decode packets received.
        Otherwise, an appropriate schema is retrieved from the registry.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Consumer().
    """

    def __init__(self, topic, schema=None, **kwargs):
        self.topic = topic
        self.kafka_kwargs = kwargs
        self.schema = schema
        self.schema_registry = SchemaRegistry.from_filesystem()

    def __enter__(self):
        self.consumer = confluent_kafka.Consumer(**self.kafka_kwargs)
        self.consumer.subscribe([self.topic])
        return self

    def __exit__(self, type, value, traceback):
        # FIXME should be properly handling exceptions here, but we aren't
        self.consumer.close()

    def poll(self):
        """Polls Kafka broker to consume topic.

        Parameters
        ----------
        decode : `boolean`
            If True, decodes data from Avro format.
        verbose : `boolean`
            If True, returns every message. If False, only raises EopError.
        """
        msg = self.consumer.poll(timeout=1e-3)

        if msg is not None:
            if msg.error():
                raise EopError(msg)
            else:
                return self.decode_message(msg)
        return

    def decode_message(self, msg):
        """Unpack and decode a received message.

        Parameters
        ----------
        msg : Kafka message
            The Kafka message resulting from calling `AlertConsumer.poll`.

        Returns
        -------
        message : `dict`
            Decoded message.

        Notes
        -----
        If this `AlertConsumer` has an associated schema, that will be used
        for decoding; otherwise, it will attempt to retrieve one from the
        registry.
        """
        raw_bytes = msg.value()
        schema_hash = struct.unpack("!I", raw_bytes[1:5])[0]
        if not self.schema:
            schema = self.schema_registry.get_by_id(schema_hash)
        else:
            schema = self.schema
        return schema.deserialize(raw_bytes[5:])
