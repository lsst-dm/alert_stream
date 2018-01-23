alert_stream
============

Mock Kafka alert stream system Kafka for sims data for use specifically on epyc machine.

Requires Docker and Docker Compose for the usage instructions below.

Usage (single host)
-------------------

Clone repo, cd into directory, and checkout appropriate branch.

**Bring up Kafka broker and Zookeeper**

From the alert_stream directory:

```
$ git checkout u/mtpatter/sims-epyc
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
$ docker build -t "sims_alerts" .
```

Note: To build your OWN image (non-shared on epyc), which you need to do whenever you make
changes to the code, you will need to name your image something else, for example, with

```
$ docker build -t "maria-sims" .
```

and refer to it in subsequent run commands below for starting containers.

This should now work:

```
$ docker run -it --rm sims_alerts python bin/sendAlertStream.py -h
```

You must rebuild your image every time you modify any of the code.

**Start producing an alert stream**

From the directory containing files of data (alerts_11575.avro, etc.),
send alerts from that visit to topic “my-stream”:

```
      docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_sender \
      -v $PWD:/home/alert_stream/data \
      sims_alerts python bin/sendAlertStream.py my-stream alerts_11575.avro
```

**Consume alert stream**

To start a consumer for printing all alerts in the stream "my-stream" to screen:

```
$ docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_printer \
      sims_alerts python bin/printStream.py my-stream
```

A template filter, which filters for objects with SNR > 5 and brighter than magnitude 18, is included in
bin/filterStream.py.  This filter outputs three fields for matching sources: alertId, ra, and dec.
Output can then be piped to a file as a csv.

```
$ docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_filter \
      sims_alerts python bin/filterStream.py my-stream > my-sources.csv
```

There currently no stamps in the simulated data.  When we have stamps, the
instruction below apply.
By default, `printStream.py` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it --rm \
      --network=alertstream_default \
      --name=$(whoami)_printer \
      -v {local path to write stamps}:/home/alert_stream/stamps:rw \
      sims_alerts python bin/printStream.py my-stream --stampDir stamps
```

Be careful not to write your output to the main shared data directory.

**Shut down and clean up**

Shutdown Kafka broker system by running the following from the alert_stream directory:

```
$ docker-compose down
```

Find your sims_alerts containers with `docker ps` and shut down with `docker kill [id]`.
Running `docker ps` will list existing running containers and can show you if someone
is already running alert streams before you try starting your own (which may not work).
