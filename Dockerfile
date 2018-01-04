# Version: 0.0.3
FROM python:3.6
LABEL maintainer "maria.t.patterson@gmail.com"
ENV REFRESHED_AT 2018-01-04

# Install library for confluent-kafka python.
WORKDIR /home
RUN git clone https://github.com/edenhill/librdkafka.git && cd librdkafka && git checkout tags/v0.9.4
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
RUN git clone https://github.com/ZwickyTransientFacility/ztf-avro-alert.git && cd ztf-avro-alert

# Add code.
RUN mkdir alert_stream
ADD . /home/alert_stream
ENV PYTHONPATH=$PYTHONPATH:/home/alert_stream/python

WORKDIR /home/alert_stream
