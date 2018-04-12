alert_stream
============

Mock Kafka alert stream system Kafka using sims data.

Requires Docker and Docker Compose for the usage instructions below.

Usage (single host)
-------------------

Clone repo, cd into directory, and checkout appropriate branch.

**Bring up Kafka broker and Zookeeper**

From the alert_stream directory:

```
$ docker-compose up -d
```

This will create a network named `alertstream_default`, or something similar, with the default driver over which the other containers will connect and will start Kafka and Zookeeper.

**Build docker image**

From the alert_stream directory:

```
$ docker build -t "alert_stream" .
```

and refer to it in subsequent run commands below for starting containers.

This should now work:

```
$ docker run -it --rm alert_stream python bin/sendAlertStream.py -h
```

You must rebuild your image every time you modify any of the code.

**Start producing an alert stream**

Send alerts of visit, e.g. 11577, to topic “my-stream”:

```
      docker run -it --rm \
      --network=alertstream_default \
      -v $PWD/data:/home/data:ro \
      alert_stream python bin/sendAlertStream.py my-stream alerts_11577.avro
```

**Consume alert stream**

To start a consumer for printing all alerts in the stream "my-stream" to screen:

```
$ docker run -it --rm \
      --network=alertstream_default \
      alert_stream python bin/printStream.py my-stream
```

A template filter, which filters for objects with SNR > 5 and brighter than magnitude 18, is included in
bin/filterStream.py.  This filter outputs three fields for matching sources: alertId, ra, and dec.
Output can then be piped to a file as a csv.

```
$ docker run -it --rm \
      --network=alertstream_default \
      alert_stream python bin/filterStream.py my-stream > my-sources.csv
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
      -v {local path to write stamps}:/home/alert_stream/stamps:rw \
      alert_stream python bin/printStream.py my-stream --stampDir stamps
```

**Shut down and clean up**

Shutdown Kafka broker system by running the following from the alert_stream directory:

```
$ docker-compose down
```

Find your alert_stream containers with `docker ps` and shut down with `docker kill [id]`.
