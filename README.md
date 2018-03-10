alert_stream
============

Code to access the ZTF alert stream on epyc remotely. 

Requires Docker and Docker Compose for the usage instructions below.

Usage (single host)
-------------------

Clone repo, cd into directory, and checkout appropriate branch.

**Bring up Kafka broker and Zookeeper**

From the alert_stream directory:

```
$ git checkout u/ebellm/remote-listener
$ docker-compose up -d
```

This will create a network named `alertstream_default`, or something similar, with the default driver over which the other containers will connect and will start Kafka and Zookeeper.

**Build docker image**

From the alert_stream directory:

```
$ docker build -t "ztf-listener" .
```

This should now work:

```
$ docker run -it --rm ztf-listener python bin/printStream.py -h
```

You must rebuild your image every time you modify any of the code.

**Consume alert stream**

To start a consumer for printing all alerts in the stream "test-stream" to screen:

```
$ docker run -it --rm \
      --network=host \
      --name=$(whoami)_printer \
      --add-host="kafka:128.95.79.19" \
      --add-host="kafka2:128.95.79.19" \
      --add-host="kafka3:128.95.79.19" \
      ztf-listener python bin/printStream.py test-stream
```

By default, `printStream.py` will not collect postage stamp cutouts.
To enable postage stamp collection, specify a directory to which files should be written with the optional flag `--stampDir <directory name>`.
If run using a Docker container, the stamps and other files written out will be collected within the container.

To collect postage stamp cutouts and output files locally, you can mount a local directory and give the Docker container write access with, e.g., the following command:

```
$ docker run -it --rm \
      --network=host \
      --name=$(whoami)_printer \
      --add-host="kafka:128.95.79.19" \
      --add-host="kafka2:128.95.79.19" \
      --add-host="kafka3:128.95.79.19" \
      -v {local path to write stamps}:/home/alert_stream/stamps:rw \
      ztf-listener python bin/printStream.py test-stream --stampDir stamps
```

Be careful not to write your output to the main shared data directory.

**Shut down and clean up**

Shutdown Kafka broker system by running the following from the alert_stream directory:

```
$ docker-compose down
```

Find your containers with `docker ps` and shut down with `docker kill [id]`.
Running `docker ps` will list existing running containers and can show you if someone
is already running alert streams before you try starting your own (which may not work).
