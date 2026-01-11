import unittest
from djanban.utils.custom_uuid import custom_uuid
import six

class TestCustomUuid(unittest.TestCase):
    def test_custom_uuid_length(self):
        uid = custom_uuid()
        self.assertGreater(len(uid), 0)

    def test_custom_uuid_is_string(self):
        uid = custom_uuid()
        self.assertIsInstance(uid, (str,))

    def test_custom_uuid_unique(self):
        uid1 = custom_uuid()
        uid2 = custom_uuid()
        self.assertNotEqual(uid1, uid2)
