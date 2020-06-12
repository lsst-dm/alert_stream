import io
import struct

import fastavro
from lsst.alert.packet import Schema


_ConfluentWireFormatHeader = struct.Struct(">bi")

latest_schema = Schema.from_file().definition


def serialize_confluent_wire_header(schema_version):
    """Returns the byte prefix for Confluent Wire Format-style Kafka messages.

    Parameters
    ----------
    schema_version : `int`
        A version number which indicates the Confluent Schema Registry ID
        number of the Avro schema used to encode the message that follows this
        header.

    Returns
    -------
    header : `bytes`
        The 5-byte encoded message prefix.

    Notes
    -----
    The Confluent Wire Format is described more fully here:
    https://docs.confluent.io/current/schema-registry/serdes-develop/index.html#wire-format
    """
    return _ConfluentWireFormatHeader.pack(0, schema_version)


def deserialize_confluent_wire_header(raw):
    """Parses the byte prefix for Confluent Wire Format-style Kafka messages.

    Parameters
    ----------
    raw : `bytes`
        The 5-byte encoded message prefix.

    Returns
    -------
    schema_version : `int`
        A version number which indicates the Confluent Schema Registry ID
        number of the Avro schema used to encode the message that follows this
        header.
    """
    _, version = _ConfluentWireFormatHeader.unpack(raw)
    return version


def serialize_alert(alert, schema=latest_schema):
    """Serialize an alert to a byte sequence for sending to Kafka.

    Parameters
    ----------
    alert : `dict`
        An alert payload to be serialized.
    schema : `dict`, optional
        An Avro schema definition describing how to encode `alert`. By default,
        the latest schema is used.

    Returns
    -------
    serialized : `bytes`
        The byte sequence describing the alert, including the Confluent Wire
        Format prefix.
    """
    buf = io.BytesIO()
    # TODO: Use a proper schema versioning system
    buf.write(serialize_confluent_wire_header(0))
    fastavro.schemaless_writer(buf, schema, alert)
    return buf.getvalue()


def deserialize_alert(alert_bytes, schema=latest_schema):
    """Deserialize an alert message from Kafka.

    Paramaters
    ----------
    alert_bytes : `bytes`
        Binary-encoding serialized Avro alert, including Confluent Wire
        Format prefix.
    schema : `dict`, optional
        An Avro schema definition describing how to encode `alert`. By default,
        the latest schema is used.

    Returns
    -------
    alert : `dict`
        An alert payload.
    """
    header_bytes = alert_bytes[:5]
    version = deserialize_confluent_wire_header(header_bytes)
    assert version == 0
    content_bytes = io.BytesIO(alert_bytes[5:])
    return fastavro.schemaless_reader(content_bytes, schema)
