MirrorMaker
============

These are files for building a MirrorMaker image used to mirror
all topics from a central Kafka hub.

To build the image run:

```
$ docker build -t "mirrormaker" .
```

These files were used to build the image mtpatter/mirrormaker
available on DockerHub.

Containers launched from this image are used in the Swarm
deployment scripts (run_mirrormakers.sh) and need the 5 sets of
consumer and producer configuration files included here.
The Swarm deployment scripts launch 5 mirrormaker instances
on 5 separate nodes.

To run containers in other contexts, uncomment lines as instructed
in the Dockerfile and provide the configuration files listed in the
runMM.sh script.
