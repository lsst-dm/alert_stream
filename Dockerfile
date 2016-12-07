# Version: 0.0.2
FROM python:3.5
MAINTAINER Maria Patterson "maria.t.patterson@gmail.com"
ENV REFRESHED_AT 2016-12-06

# Install library for confluent-kafka python.
WORKDIR /home
RUN git clone https://github.com/edenhill/librdkafka.git && cd librdkafka && git checkout tags/v0.9.2
WORKDIR /home/librdkafka
RUN ./configure && make && make install
ENV LD_LIBRARY_PATH /usr/local/lib

# Pip installs.
RUN pip install confluent-kafka
RUN pip install avro-python3
RUN pip install Cython
RUN pip install fastavro

# Get schemas and template data. # TODO update to checkout master when schema is updated
WORKDIR /home
RUN git clone https://github.com/lsst-dm/sample-avro-alert.git && cd sample-avro-alert && git checkout tickets/DM-7451

# Add code.
RUN mkdir alert_stream
ADD . /home/alert_stream
ENV PYTHONPATH=$PYTHONPATH:/home/alert_stream/python

WORKDIR /home/alert_stream
