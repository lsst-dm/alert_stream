alert_stream
============

Mock alert stream distribution system using Kafka producers and consumers.

This uses [Confluent's Kafka client for Python](https://github.com/confluentinc/confluent-kafka-python), which wraps the librdkafka C library. The librdkafka C library is installed into the Docker container built with the accompanying Dockerfile.

Requires Docker and Docker Compose.

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

Start an alert stream to topic “my-stream” with 1000 alerts:

```
$ docker run -it --network=host alert_stream python bin/sendAlertStream.py my-stream 1000
```

**Consume alert stream**

To start a consumer for monitoring "my-stream":

```
$ docker run -it --network=host alert_stream python bin/monitorAlertStream.py my-stream monitor-group
```

To start a consumer for printing all alerts in the stream "my-stream":

```
$ docker run -it --network=host alert_stream python bin/printAlertStream.py my-stream echo-group
```

Or to just run a Python terminal in the Docker environment:

```
$ docker run -it alert_stream python
```

**Shut down and clean up**

Shutdown Kafka broker system:

```
$ docker-compose down
```

Find alert_stream container names with `docker ps` and shut down with `docker stop [name]`.
