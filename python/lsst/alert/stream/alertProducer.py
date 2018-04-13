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
    schema : Avro schema
        The writer Avro schema for encoding data. Optional.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Producer().
    """

    def __init__(self, topic, schema_files=None, **kwargs):
        self.producer = confluent_kafka.Producer(**kwargs)
        self.topic = topic
        if schema_files is not None:
            self.alert_schema = avroUtils.combineSchemas(schema_files)

    def send(self, data, encode=False):
        """Sends a message to Kafka stream.

        Parameters
        ----------
        data : message content
            Data containing message content.  If encode is True, expects JSON.
        encode : `boolean`
            If True, encodes data to Avro format. If False, sends data raw.
        """
        if encode is True:
            avro_bytes = avroUtils.writeAvroData(data, self.alert_schema)
            raw_bytes = avro_bytes.getvalue()
            self.producer.produce(self.topic, raw_bytes)
        else:
            self.producer.produce(self.topic, data)

    def flush(self):
        return self.producer.flush()
