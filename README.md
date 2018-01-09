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

**Build docker container**

From the alert_stream directory:

```
$ docker build -t "sims_alerts" .
```

This should now work:

```
$ docker run -it sims_alerts python bin/sendAlertStream.py -h
```

You must rebuild your container every time you modify any of the code.

**Start producing an alert stream**

From the directory containing files of data (alerts_11575.avro, etc.),
send alerts from that visit to topic “my-stream”:

```
      docker run -it \
      --network=alertstream_default \
      -v $PWD:/home/alert_stream/data \
      sims_alerts python bin/sendAlertStream.py my-stream alerts_11575.avro
```

**Consume alert stream**

To start a consumer for printing all alerts in the stream "my-stream" to screen:

```
$ docker run -it \
      --network=alertstream_default \
      sims_alerts python bin/printStream.py my-stream
```

There currently no stamps in the simulated data.  When we have stamps, the
instruction below apply.
By default, `printStream.py` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it \
      --network=alertstream_default \
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
