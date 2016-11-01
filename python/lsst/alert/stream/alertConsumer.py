from __future__ import print_function
import sys
import confluent_kafka
from . import avroUtils
from . import kafkaUtils


__all__ = ['AlertConsumer']


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
                return kafkaUtils.writeEopNotice(msg)
            else:
                if verbose is True:
                    return msg.value()
                else:
                    pass

        else:
            try:
                msg = self.consumer.poll()

                if msg.error():
                    return kafkaUtils.writeEopNotice(msg)
                else:
                    if verbose is True:
                        return kafkaUtils.decodeMessage(msg, self.alert_schema)
                    else:
                        pass

            except IndexError:
                sys.stderr.write('%% Data cannot be decoded.\n')
                pass
