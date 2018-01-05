alert_stream
============

Mock Kafka alert stream system Kafka for ZTF data for use specifically on epyc machine.

Requires Docker and Docker Compose for the usage instructions below.

Usage (single host)
-------------------

Clone repo, cd into directory, and checkout appropriate branch.

**Bring up Kafka broker and Zookeeper**

From the alert_stream directory:

```
$ docker-compose up -d
```

This will create a network named `alertstream_default`, or something similar, with the default driver over which the other containers will connect.

**Build docker container**

From the alert_stream directory:

```
$ docker build -t "epyc_alerts" .
```

This should now work:

```
$ docker run -it epyc_alerts python bin/sendAlertStream.py -h
```

You must rebuild your container every time you modify any of the code.

**Start producing an alert stream**

From the directory containing dates of data (20171227, etc.),
send alerts to topic “my-stream” starting with a certain date and pausing for 5 seconds between visits:

```
      docker run -it \
      --network=alertstream_default \
      -v $PWD:/home/alert_stream/data \
      epyc_alerts python bin/sendAlertStream.py my-stream 20171227 5
```

**Consume alert stream**

To start a consumer for printing all alerts in the stream "my-stream" to screen:

```
$ docker run -it \
      --network=alertstream_default \
      epyc_alerts python bin/printStream.py my-stream
```

By default, `printStream.py` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it \
      --network=alertstream_default \
      -v {local path to write stamps}:/home/alert_stream/stamps:rw \
      epyc_alerts python bin/printStream.py my-stream --stampDir stamps
```

Be careful not to write your output to the main shared data directory.

**Shut down and clean up**

Shutdown Kafka broker system by running the following from the alert_stream directory:

```
$ docker-compose down
```

Find your epyc_alerts containers with `docker ps` and shut down with `docker kill [id]`.
