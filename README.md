alert_stream
============

Mock alert stream distribution system using Kafka producers and consumers.

This uses [Confluent's Kafka client for Python](https://github.com/confluentinc/confluent-kafka-python), which wraps the librdkafka C library. The librdkafka C library is installed into the Docker container built with the accompanying Dockerfile.

Requires Docker and Docker Compose for the usage instructions below.

Usage
-----

Clone repo, cd into directory, and checkout appropriate branch.

**Bring up Kafka broker and Zookeeper**

From the alert_stream directory:

```
$ docker-compose up -d
```

**Build docker container**

From the alert_stream directory:

```
$ docker build -t "alert_stream" .
```

This should now work:

```
$ docker run -it alert_stream python bin/sendAlertStream.py -h
```

**Start producing an alert stream**

Start an alert stream to topic “my-stream” with 100 alerts:

```
$ docker run -it --network=host alert_stream python bin/sendAlertStream.py my-stream 100
```

To exclude sending postage stamp cutouts, add the optional flag to the python command `--no-stamps`.

Avro encoding is turned on by default to enforce a schema. To turn this off, add the optional flag `--encode-off`.

**Consume alert stream**

To start a consumer for monitoring "my-stream", which will consume a stream and print only End of Partition status messages:

```
$ docker run -it --network=host alert_stream python bin/monitorStream.py my-stream monitor-group
```

To start a consumer for printing all alerts in the stream "my-stream":

```
$ docker run -it --network=host alert_stream python bin/printStream.py my-stream echo-group
```

By default, `printStream.py` will not collect postage stamp cutouts. To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`. If run using a Docker container, the stamps will be collected within the container.

Avro decoding is turned on by default. To turn this off, add the optional flag `--decode-off`.

**Shut down and clean up**

Shutdown Kafka broker system:

```
$ docker-compose down
```

Find alert_stream container names with `docker ps` and shut down with `docker stop [name]`.

Notes
-----

Note well that currently the repo contents are copied into the Docker image on build, so any changes to the code require rebuilding the image if using Docker.

Also note that consumers with the same group ID share a stream so that only one consumer in the group will receive a message (as in a queue). To run multiple consumers each consuming all messages, each consumer needs a different group ID.

**On Docker**

To just run a Python terminal in the Docker environment:

```
$ docker run -it alert_stream python
```

To collect postage stamp cutouts to your local machine, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it --network=host -v $PWD/stamps:/home/alert_stream/stamps:rw alert_stream python bin/printStream.py my-stream echo-group --stampDir stamps
```
