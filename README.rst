############
alert_stream
############

This package provides a demonstration of the LSST Alert Distribution Service.
The Alert Distribution Service provides a mechanism for rapidly disseminating and filtering notifications of transient and variable sources observed by LSST.
The service is described in detail in `DMTN-093`_.
This repository provides instructions, code and sample data for creating, filtering, and consuming alert streams following the conventions we expect to adopt for LSST.
It should be used in conjunction with the `lsst-dm/sample-avro-alert`_ repository, which provides details of, and code for working with, LSST alert packets.

.. _DMTN-093: https://dmtn-093.lsst.io/
.. _lsst-dm/sample-avro-alert: https://github.com/lsst-dm/sample-avro-alert

Prerequisites
=============

- Cloning this repository requires `Git LFS`_ (Large File Storage) support.
  Refer to the `DM Developer Guide`_ for more information.
- `Docker`_ and `Docker Compose`_ are required to create and manage the services within this repository, including running all of the examples below.

.. _Git LFS: https://git-lfs.github.com
.. _DM Developer Guide: https://developer.lsst.io/git/git-lfs.html
.. _Docker: https://www.docker.com
.. _Docker Compose: https://docs.docker.com/compose/overview/

Orientation
===========

This package provides a number of command-line tools which demonstrate the design and capabilities of the LSST Alert Distribution and Alert Filtering systems.
Specifically:

``sendAlertStream.py``
   Sends a stream of alert packets to the `Apache Kafka`_ streaming platform.
   This stream is designed to resemble the raw, unfiltered output of the LSST Alert Distribution system, as will be provided to community brokers during LSST operations.
   Note that it is provided as a demonstration, and should not be regarded as normative.

``filterStream.py``
   Filters the stream being produced by ``sendAlertStream.py``, resulting in a new stream containing only a subset of the alerts.
   This is intented to demonstrate the functionality of the Alert Filtering Service.

``printStream.py``
   Receives an alert stream (either the raw stream, as produced by ``sendAlertStream.py``, or a filtered version thereof) and prints the contents to the console.
   This demonstrates how a subscriber (either a broker, or a scientist end-user) can access and process an alert stream using Kafka.

``monitorStream.py``
   Monitors an alert stream and prints status information to the console.

Ultimately, some users may want to write their own clients to consume alert streams.
For more information on what this involves, refer to the Technology Summary, below.

.. _Apache Kafka: https://kafka.apache.org

Usage Instructions
==================

To deploy this service on a single host, first clone this repository, change into the cloned directory, and (if applicable) check out the relevant branch, then follow the instructions below.

The service may also be deployed over multiple hosts using Docker Swarm.
See ``swarm/README.md`` for instructions.

Bring up Kafka and Zookeeper
----------------------------

From the alert_stream directory::

   $ docker-compose up -d

This will create a network named ``alert_stream_default`` with the default driver over which the other containers will connect and will start Kafka and Zookeeper.

Build the Docker image
----------------------

From the ``alert_stream`` directory::

   $ docker build -t "alert_stream" .

and refer to it in subsequent run commands below for starting containers.

This should now work::

   $ docker run -it --rm alert_stream python bin/sendAlertStream.py -h

You must rebuild your image every time you modify any of the code, unless you mount local code as a volume in the container.

Start producing an alert stream
-------------------------------

Sample data is included in the ``data`` directory.  You can also mount a local volume of data by replacing ``$PWD/data`` in the command below with an appropriate path to other alert data.

Send bursts of alerts at expected visit intervals to topic ``my-stream``::

   $ docker run -it --rm \
     --network=alert_stream_default \
     -v $PWD/data:/home/alert_stream/data:ro \
     alert_stream python bin/sendAlertStream.py kafka:9092 my-stream

Filter the alert stream
-----------------------

Template filters, which filters for objects with SNR > 5 and brighter than magnitude 20, are included in ``filters.py``.
These filters output to a new stream with the name of the filter class.

The following will run filter 1, producing a filtered stream named ``Filter001``::

  $ docker run -it --rm \
    --network=alert_stream_default \
    alert_stream python bin/filterStream.py kafka:9092 my-stream 1

Consume the alert stream
------------------------

To start a consumer for printing all alerts in the stream ``Filter001`` to screen::

   $ docker run -it --rm \
     --network=alert_stream_default \
     alert_stream python bin/printStream.py kafka:9092 Filter001 1

To start a consumer that will show the status (number of alerts, etc.) of stream ``Filter001``::

   $ docker run -it --rm \
     --network=alert_stream_default \
     alert_stream python bin/monitorStream.py kafka:9092 Filter001

There currently no “postage stamp” cut-out images in the simulated data.
When we have stamps, the instructions below apply.
By default, ``printStream.py`` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag ``--stampDir <directory name>``.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command::

   $ docker run -it --rm \
     --network=alert_stream_default \
     -v {local path to write stamps}:/home/alert_stream/stamps:rw \
     alert_stream python bin/printStream.py kafka:9092 Filter001 1 --stampDir stamps

Shut down and clean up
----------------------

Shut down the Kafka broker system by running the following from the ``alert_stream`` directory::

   $ docker-compose down

Find your alert_stream containers with ``docker ps`` and shut down with ``docker kill [id]``.

.. _tech-summary:

Technology Summary
==================

The LSST Alert Distribution Service distributes alert packets, formatted using `Apache Avro`_ , using the `Apache Kafka`_ streaming platform.
Each alert is transmitted as a separate Kafka message.
Schemas are not sent with the alerts: the consumer is assumed to receive a copy of the schema through some other mechanism (currently by cloning https://github.com/lsst-dm/sample-avro-alert).
Alerts are packaged using the `Confluent Wire Format`_.
This means that the first byte of the message received may be ignored, the next four constitute a “schema identifier” (which may be used to identify the schema used to write the packet) and the remainder constitute the alert data serialized in Avro format.
Intepreting the packet in (for example) Python may then be done as follows::

   import struct

   raw_alert_bytes = ... # the data received from Kafka
   intial_byte = struct.unpack("!b", raw_alert_bytes[0])  # should always be 0
   schema_id = struct.unpack("!I", raw_alert_bytes[1:5])  # schema identifier
   avro_bytes = raw_alert_bytes[5:]                       # feed to your Avro deserializer

.. _Apache Avro: https://avro.apache.org
.. _Apache Kafka: https://kafka.apache.org
.. _Confluent Wire Format: https://docs.confluent.io/current/schema-registry/docs/serializer-formatter.html#wire-format
