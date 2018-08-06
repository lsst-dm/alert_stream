alert_stream
============

Mock Kafka alert stream system Kafka using sims data.

Requires Docker and Docker Compose for the usage instructions below.

Git LFS
-------

To clone and use this repository, you'll need Git Large File Storage (LFS).

Our [Developer Guide](https://developer.lsst.io/tools/git_lfs.html)
explains how to set up Git LFS for LSST development.

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

You must rebuild your image every time you modify any of the code,
unless you mount local code as a volume in the container.

**Start producing an alert stream**

Sample data is included in the data directory.
You can also mount a local volume of data following the instructions below.

Send bursts of alerts at expected visit intervals to topic “my-stream”:

```
      docker run -it --rm \
      --network=alertstream_default \
      -v $PWD/data:/home/alert_stream/data:ro \
      alert_stream python bin/sendAlertStream.py kafka:9092 my-stream
```

**Filter the alert stream**

Template filters, which filters for objects with SNR > 5 and brighter than magnitude
20, are included in filters.py.  These filters output to a new stream with the
name of the filter class.

The following will run filter 1, producing a filtered streams named
"Filter001":

```
$ docker run -it --rm \
      --network=alertstream_default \
      alert_stream python bin/filterStream.py kafka:9092 my-stream 1
```

**Consume alert stream**

To start a consumer for printing all alerts in the stream "Filter001" to screen:

```
$ docker run -it --rm \
      --network=alertstream_default \
      alert_stream python bin/printStream.py kafka:9092 Filter001
```

To start a consumer that will show the status (number of alerts, etc.)
of stream "Filter001":

```
$ docker run -it --rm \
      --network=alertstream_default \
      alert_stream python bin/monitorStream.py kafka:9092 Filter001
```

There currently no stamps in the simulated data.  When we have stamps, the
instructions below apply.
By default, `printStream.py` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it --rm \
      --network=alertstream_default \
      -v {local path to write stamps}:/home/alert_stream/stamps:rw \
      alert_stream python bin/printStream.py kafka:9092 Filter001 --stampDir stamps
```

**Shut down and clean up**

Shutdown Kafka broker system by running the following from the alert_stream directory:

```
$ docker-compose down
```

Find your alert_stream containers with `docker ps` and shut down with `docker kill [id]`.
