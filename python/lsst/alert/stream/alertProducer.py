from __future__ import print_function
import confluent_kafka
from . import avroUtils

__all__ = ['AlertProducer']


class AlertProducer(object):
    """Alert stream producer with Kafka.

    Parameters
    ----------
    topic : `str`
        The name of the topic stream for writing.
    schema : `lsst.alert.packet.Schema`, optional
        The Avro schema for encoding data. Although one is not required to
        construct the producer, you can't begin sending data until one has
        been supplied.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Producer().
    """

    def __init__(self, topic, schema=None, **kwargs):
        self.producer = confluent_kafka.Producer(**kwargs)
        self.topic = topic
        self.schema = schema

    def send(self, data):
        """Sends a message to Kafka stream.

        The message is encoded following the schema embedded in this producer.

        Parameters
        ----------
        data : `dict`
            Message content. Must comply with the schema configured in this
            `AlertProducer`.
        """
        avro_bytes = self.schema.serialize(data)
        self.producer.produce(self.topic, avro_bytes)

    def flush(self):
        return self.producer.flush()
