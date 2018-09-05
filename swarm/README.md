Mini-broker Swarm deployment for isolated containerized filters
--------------------------------------------------------------

These are Swarm deployment scripts for a version of the
mini-broker running a one-container-per-filter setup.
This design is updated from the design described in DMTN-081
[https://dmtn-028.lsst.io](https://dmtn-028.lsst.io), which
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
