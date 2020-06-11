import unittest

from lsst.alert.stream import serialization


class TestSerialization(unittest.TestCase):
    def test_serialize_alert_round_trip(self):
        alert = mock_alert(1)
        serialized = serialization.serialize_alert(alert)
        deserialized = serialization.deserialize_alert(serialized)
        self.assertEqual(1, deserialized["alertId"])


def mock_alert(alert_id):
    """Generate a minimal mock alert. """
    return {
        "alertId": alert_id,
        "diaSource": {
            # Below are all the required fields. Set them to zero.
            "midPointTai": 0,
            "diaSourceId": 0,
            "ccdVisitId": 0,
            "filterName": "",
            "programId": 0,
            "ra": 0,
            "decl": 0,
            "x": 0,
            "y": 0,
            "apFlux": 0,
            "apFluxErr": 0,
            "snr": 0,
            "psFlux": 0,
            "psFluxErr": 0,
            "flags": 0,
        }
    }
