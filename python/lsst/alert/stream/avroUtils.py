"""Utilities for manipulating Avro data and schemas.
"""

import io
import json
import avro.schema
import avro.io


__all__ = ['combineSchemas', 'writeAvroData', 'readAvroData']


def _loadSingleAvsc(file_path, names):
    """Load a single avsc file.
    """
    with open(file_path) as file_text:
        json_data = json.load(file_text)
    schema = avro.schema.SchemaFromJSONData(json_data, names)
    return schema


def combineSchemas(schema_files):
    """Combine multiple nested schemas into a single schema.

    Parameters
    ----------
    schema_files : `list`
        List of files containing schemas.  If nested, most internal schema must be first.

    Returns
    -------
    `avro.schema.RecordSchema`
        Avro schema
    """
    known_schemas = avro.schema.Names()

    for s in schema_files:
        schema = _loadSingleAvsc(s, known_schemas)
    return schema


def writeAvroData(json_data, avro_schema):
    """Encode json into Avro format given a schema.

    Parameters
    ----------
    json_data : `dict`
        The JSON data containing message content.
    avro_schema : Avro schema
        The writer Avro schema for encoding data.

    Returns
    -------
    `_io.BytesIO`
        Encoded data.
    """
    writer = avro.io.DatumWriter(avro_schema)
    bytes_io = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_io)
    writer.write(json_data, encoder)
    return bytes_io


def readAvroData(bytes_io, avro_schema):
    """Read data and decode with a given Avro schema.

    Parameters
    ----------
    bytes_io : `_io.BytesIO`
        Data to be decoded.
    avro_schema : Avro schema
        The reader Avro schema for decoding data.

    Returns
    -------
    `dict`
        Decoded data.
    """
    raw_bytes = bytes_io.getvalue()
    bytes_reader = io.BytesIO(raw_bytes)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    reader = avro.io.DatumReader(avro_schema)
    message = reader.read(decoder)
    return message
