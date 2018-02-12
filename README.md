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
$ git checkout u/mtpatter/ztf-epyc
$ docker-compose up -d
```

This will create a network named `alertstream_default`, or something similar, with the default driver over which the other containers will connect and will start Kafka and Zookeeper.

Note: To start your OWN broker (non-shared on epyc) from which to send and read a stream, you will
need to do two things.

1. In the docker-compose.yml file, change the service names of "kafka" and "zookeeper" to something like
"maria-kafka" and "maria-zookeeper."
2. In the Python files for sending and receiving the stream, change the configuration of Kafka
bootstrap.servers from "kafka:9092" to "maria-kafka:9092."

**Build docker image**

From the alert_stream directory:

```
$ docker build -t "epyc_alerts" .
```

Note: To build your OWN image (non-shared on epyc), which you need to do whenever you make
changes to the code, you will need to name your image something else, for example, with

```
$ docker build -t "maria-ztf" .
```

and refer to it in subsequent run commands below for starting containers.

This should now work:

```
$ docker run -it --rm epyc_alerts python bin/sendAlertStream.py -h
```

You must rebuild your image every time you modify any of the code.

**Start producing an alert stream**

Send alerts to topic “my-stream” starting with a certain date, e.g. 20171227 and pausing for 5 seconds between visits:

```
      docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_sender \
      -v /data/scratch/ebellm/ztf_alerts/ztfweb.ipac.caltech.edu:/home/data:ro \
      epyc_alerts python bin/sendAlertStream.py my-stream 20171227 5
```

**Consume alert stream**

To start a consumer for printing all alerts in the stream "my-stream" to screen:

```
$ docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_printer \
      epyc_alerts python bin/printStream.py my-stream
```

By default, `printStream.py` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_printer \
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
Running `docker ps` will list existing running containers and can show you if someone
is already running alert streams before you try starting your own (which may not work).
