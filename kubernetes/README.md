Kubernetes Deployment
=====================

The scripts here will deploy the `alert_stream` alert producer,
100 filters, and consumers of the full stream and filtered
streams.

Follow the commands in `run.sh`.

The yaml files are written for deployment on NCSA's
infrastructure, using the local Docker registry image
`lsst-kub001:5000/alert_stream`.  
For deployment in other compute environments, change
the image field to use the image accessible to you.

The alert producer can generate alerts from the sample
data included in this repo or a mounted volume of
alerts located as set in the host path in the
alert-data yaml file, as described in `run.sh`.

The consumers of the filtered streams are set to print
every alert (20 per visit).  The consumer of the full
stream will print every 100th alert.  This can
be modified in the arguments in each deployment script.

Output can be viewed by finding the pod of interest with

```
kubectl get pods
```

and running

```
kubectl logs <podname>
```
