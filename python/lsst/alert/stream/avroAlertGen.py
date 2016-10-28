from __future__ import print_function
import time
import sys
from . import avroUtils

__all__ = ['AvroAlertGen']


class AvroAlertGen:
    """Populates mock alert stream for a single CCD given an Avro schema and template data in json format.

    Parameters
    ----------
    json_data : `dict`
        The JSON data containing alert content.
    schema : Avro schema
        The writer Avro schema for encoding data.
    ccdnum : `int`
        An identifier for the CCD.
    """

    def __init__(self, json_data, schema, ccdnum=1):
        self.ccdnum = ccdnum
        self.avro_bytes = avroUtils.writeAvroData(json_data, schema)
        self.raw_bytes = self.avro_bytes.getvalue()

    def sendAlerts(self, producer, topic, alertnum):
        """Sends a given number of alerts to a topic stream.

        Parameters
        ----------
        producer : `confluent_kafka.Producer`
            Configures Kafka producer for writing alerts.
        topic : `str`
            The name of the topic stream for writing.
        alertnum : `int`
            The number of alerts to produce.
        """
        totsize = alertnum*sys.getsizeof(self.raw_bytes)
        print("topic:{:s}, ccdnum:{:d}, numalerts:{:d}, sizebytes:{:d}, time:{:.3f}".format(topic,
                                                                                            self.ccdnum,
                                                                                            alertnum,
                                                                                            totsize,
                                                                                            time.time()))
        for i in range(alertnum):
            producer.produce(topic, self.raw_bytes)
        producer.flush()
