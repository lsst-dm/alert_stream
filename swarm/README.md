Mini-broker Swarm deployment for isolated containerized filters
===============================================================

Overview
--------

These are Swarm deployment scripts for a version of the
mini-broker running a one-container-per-filter setup.
This design is updated from the design described in DMTN-081
[https://dmtn-081.lsst.io](https://dmtn-081.lsst.io), which
runs multiple filters in the same container.
To deploy a prototype of the full mini-broker with 100 consumers
(end users) and 100 individual filters each in their own container,
run the `deploy_all.sh` script.
This will deploy the following setup on a total of 12 Swarm nodes
(one Swarm manager node running the main Kafka hub and 11 Swarm worker nodes - an alert producer node, five "filterer" nodes, and 5 consumer nodes).
This prototype was deployed on 12 AWS m4.4xlarge ec2 instances,
which have 16 vCPU, 64 GiB memory, and 2,000 Mbps dedicated
EBS bandwidth.

* A main Kafka/Zookeeper hub on the Swarm manager node that receives the full alert stream and runs by itself on the manager node
* A single alert producer running on its own separate node that sends the full stream of alerts to the main Kafka/Zookeeper hub
* Five downstream Kafka/Zookeepers for feeding the filterers, which mirror the full stream and run each on a separate node
* 100 stream filterer containers split into 20 on each of the five Kafka/Zookeeper mirror nodes, which read the full stream and send filtered alert streams back to the co-located Kafka mirror
* 100 consumers of the filtered streams running as 20 separate containers on five separate nodes and read from the Kafka mirrors

Required are `consumernodes.txt`, `filternodes.txt`, and `sendernodes.txt`,
each with the Swarm IDs of the nodes on which to run the different components
on separate lines.
The consumer and filter nodes files should each have the IDs of five unique nodes,
so that each node will run 20 consumer or 20 filter containers, for a total
of 100 consumers and 100 filters.
The sender node file needs one Swarm ID on which to place a single
alert producer sending alerts 10,000 alerts per visit (every 39 seconds),
which is the performance requirement set by DMS-REQ-0343 at the expected
visit interval.

Performance
-----------

This design has the advantage of being able to run 100 filters without
each filter having to read its own full copy of the stream over a network.
With groups of 20 filters on five Kafka mirror nodes, the network
needs only to support enough bandwidth for the alert producer to the
main Kafka hub and five full streams feeding each of the mirror nodes.
Each Kafka mirror node receives one copy of the full stream and acts
independently of the other Kafka mirror nodes.
Individual filters read from and write to co-located Kafka mirrors.
Each filter runs isolated in its own container and does not interact
with other filters.

A disadvantage to this design is that each filter container locally
reads a full copy of the stream and subsequently fewer filters may be
able to run on a single node.
Each filter container could conceivably run multiple filters in parallel
sharing a single copy of the full stream, but those filters may interact
with / potentially slow each other.

The following describes timing performance for a simulation with 18 visits:

* Max time for the alert producer to serialize one visit of 10,000 alerts and finish sending to Kafka - 15.76 seconds
* Mean time from the alert producer finishing sending the last alert of a visit to Kafka to a filterer finishing processing all alerts in a visit - 0.25 seconds
* Mean time from the alert producer starting to send alerts to the 20th filtered alert to be received by an end consumer - 5.28 seconds

The above timing numbers are for 20 filters per node, which is the default
for the included scripts.
Up to 50 filters have been successfully deployed per node on AWS m4.4xlarge
ec2 instances for a total of 250 simultaneous filters.

For the same experiments with 50 filters per node, the following describes the
timing performance:

* Time for the alert producer to serialize one visit of 10,000 alerts and finish
sending to Kafka - 16.4 seconds mean, 16.5 seconds max
* Time between the alert producer starting to send a visit of alerts and the last
filtered alert (20th) being received by a consumer - 16.5 seconds mean,
38.7 seconds max
* Time between the alert producer starting to send a visit of alerts and a filter
finishing processing of the whole visit - 25.7 seconds mean, 31.7 seconds max
* Time between the alert producer finishing sending all alerts and a filter
finishing processing all alerts - 1.7 seconds mean, 15.4 seconds max

Compared with the prototype of the alert distribution without filters described
in DMTN-028, there is no noticeable effect on / slowing of the system's
ability to keep up with the alert rate produced to Kafka for distribution,
meaning that the alert producer is not slowed as was observed when a large number
of consumers received alerts simultaneously.
A filter adds only about a quarter of a second to the alert distribution
component of the pipelines.
The filters used here are a simple magnitude cut- more complicated filters
may add to this time.

Note that the time for the alert producer to serialize and finish sending alerts
is high because the alerts are sent from a single producer.
Splitting up alert production into 200 producers (about 1 per CCD) acting in
parallel significantly decreases this time but was not tested here.
(See DMTN-028 [https://dmtn-028.lsst.io](https://dmtn-028.lsst.io).)
Also note that here the end consumers receive the last (20th) selected alert
before the alert producer finishes sending the last alert in a visit.
This is because many alerts are selected by the filters used here.

Deployment instructions for AWS
-------------------------------

A full mini-broker can be deployed on any Swarm or on AWS
using AWS's CloudFormation service.
A template for a Docker for AWS CloudFormation deployment is included here
in the file Docker.tmpl.
To deploy a Docker for AWS stack, navigate to the CloudFormation service page,
go to "Create new stack,"
and upload the Docker template or instead navigate directly to [https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=Docker&templateURL=https://editions-us-east-1.s3.amazonaws.com/aws/stable/Docker.tmpl](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=Docker&templateURL=https://editions-us-east-1.s3.amazonaws.com/aws/stable/Docker.tmpl).

The following are appropriate choices for stack parameters:

* Number of Swarm managers = 1
* Number of Swarm worker nodes = 11
* Swarm manager instance type? = m4.4xlarge
* Agent worker instance type? = m4.4xlarge

The rest can be left to the default options.

Once the stack is created, navigate to "Running Instances" on the ec2 service
page and identify the Docker-Manager machine.
The Public DNS (IPv4) under the description of that machine gives you the
address to which you can ssh as the user "docker" with the ssh key you
used to generate your stack, for example:

```
$ ssh docker@ec2-99-999-9-99.us-east-2.compute.amazonaws.com
```
You should see a "Welcome to Docker!" message.
Copy all scripts from this swarm directory to your manager machine:

```
$ scp * docker@ec2-99-999-9-99.us-east-2.compute.amazonaws.com
```

The deployment scripts need input files listing the nodes on which to run
the different components of the mini-broker.
To list the IDs and statuses of the available Docker Swarm nodes, run the
following command:

```
$ docker node ls
```

One of these nodes will be listed as "Leader" under "Management Status."
The deployment scripts will automatically choose this Leader node for running
the central Kafka and Zookeeper hub.
The other 11 nodes will be Swarm worker nodes.
For this setup of 1+11 Swarm nodes, you can choose five nodes to each house
the downstream Kafka+Zookeeper+MirrorMaker hubs and corresponding group of
20 filters, five nodes to each house 20 consumers, and one node containing
an alert producer generating 10,000 alerts per visit every 39 seconds.

Copy the selected node IDs into the files `filternodes.txt`,
`consumernodes.txt`, and `sendernodes.txt`, one ID per line.
The deployment scripts can automatically size a mini-broker depending on the
number of nodes listed in these files, up to the number of filter classes
included in the alert_stream image.
For example, to run only Filter001-Filter040, only list two nodes
in the `filternodes.txt` and `consumernodes.txt` files.
The Kafka and Zookeeper Docker images come from the Docker Hub
organization 'confluentinc' and the MirrorMaker and alert_stream
Docker images currently come from the organization 'mtpatter', under the repos
`mirrormaker` and `sims-dev`.
In order to use the alert_stream image built locally from the Dockerfile included
here instead of Docker Hub, a private registry must be set up so that
all nodes of the Swarm are able to access the Docker image.
See the `deploy_all.sh` and other scripts for details on how the components
are created.  

Run the main deployment script to bring up the full mini-broker:

```
$ ./deploy_all.sh
```

Everything that goes to stdout is written to the Docker service logs.
For Swarms on Docker for AWS, these logs are accessible via the
CloudWatch AWS service.
To view them, navigate to the CloudWatch service homepage, choose
"Logs" and then choose the name of the CloudFormation stack under "Log Groups."
You will find one log file per container.
These can be exported by selecting the stack on the "Logs" page
and choosing "Export data to Amazon S3" under the "Actions" button.
The logs can then be downloaded from your S3 bucket.

When finished, you can shut down all services by running the following:

```
$ docker service rm $(docker service ls -q)
```

To tear down the stack, navigate to CloudFormation and choose "Delete Stack"
under "Actions" to clean up.
