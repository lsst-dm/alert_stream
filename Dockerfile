# Version: DM-14704
FROM python:3.6
LABEL maintainer "maria.t.patterson@gmail.com"
ENV REFRESHED_AT 2018-06-07

# Pip installs.
RUN pip install 'confluent-kafka>=0.11.4'
RUN pip install avro-python3
RUN pip install Cython
RUN pip install fastavro

# Get schemas and template data. # TODO update to checkout master when schema is updated
WORKDIR /home
RUN git clone https://github.com/lsst-dm/sample-avro-alert.git && cd sample-avro-alert && git checkout tickets/DM-8160

# Add code.
RUN mkdir alert_stream
ADD . /home/alert_stream
ENV PYTHONPATH=$PYTHONPATH:/home/alert_stream/python

WORKDIR /home/alert_stream
