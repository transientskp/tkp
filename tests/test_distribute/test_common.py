import filecmp
import tempfile
import shutil
import unittest2 as unittest
from tkp.distribute.common import serialize, deserialize
from tkp.testutil.data import casa_table


class TestSerialize(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def test_code_decode(self):
        encoded = serialize(casa_table)
        decoded_path = deserialize(encoded, path=self.path)
        comp = filecmp.dircmp(casa_table, decoded_path)
        assert(len(comp.diff_files) == 0)
        assert(len(comp.funny_files) == 0)
