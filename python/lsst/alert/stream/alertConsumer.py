from __future__ import print_function
import sys
import confluent_kafka
from . import kafkaUtils


__all__ = ['AlertConsumer']


class AlertConsumer(object):
    """Creates an alert stream Kafka consumer for a given topic.

    Parameters
    ----------
    topic : `str`
        Name of the topic to subscribe to.
    **kwargs
        Keyword arguments for configuring confluent_kafka.Consumer().
    """

    def __init__(self, topic, **kwargs):
        self.consumer = confluent_kafka.Consumer(**kwargs)
        self.consumer.subscribe([topic])

    def printAlertStream(self, schema):
        """Polls Kafka broker and decodes messages according to a given schema for printing.

        Parameters
        ----------
        schema : Avro schema
            The reader Avro schema for decoding data.
        """
        try:
            while True:
                msg = self.consumer.poll()

                if msg is None:
                    continue
                else:
                    kafkaUtils.printAllMessages(msg, schema)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
            sys.exit

    def watchAllAlerts(self):
        """Polls Kafka broker, monitors for messages, and writes receipt notes.
        """
        try:
            while True:
                msg = self.consumer.poll()

                if msg is None:
                    continue
                else:
                    kafkaUtils.writeAllReceipts(msg)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
            sys.exit

    def watchBatches(self):
        """Polls Kafka broker, monitors for batches, and writes receipt notes.
        """
        try:
            while True:
                msg = self.consumer.poll()

                if msg is None:
                    continue
                elif msg.error():
                    kafkaUtils.writeEopNotice(msg)
                else:
                    continue

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
            sys.exit
