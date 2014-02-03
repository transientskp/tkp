import unittest
import os
import tempfile
import shutil
from ConfigParser import SafeConfigParser
import tkp
import tkp.accessors
import tkp.inject
from tkp.testutil.data import DATAPATH
from tkp.conf import parse_to_dict
from tkp.testutil.data import default_header_inject_config
from tkp.accessors.lofaraccessor import LofarAccessor
from tkp.accessors.dataaccessor import DataAccessor

fits_file = os.path.join(DATAPATH, 'missingheaders.fits')

class TestInject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_dir = os.getcwd()
        cls.temp_dir = tempfile.mkdtemp()
        cls.fixed_file = os.path.join(cls.temp_dir, 'fixed.fits')
        shutil.copy(fits_file, cls.fixed_file)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.start_dir)
        shutil.rmtree(cls.temp_dir)

    def test_no_injection(self):
        # Without injection the file cannot be opened as a LOFAR image
        # We fall back to opening it as plain DataAccessor.
        accessor = tkp.accessors.open(fits_file)
        self.assertTrue(isinstance(accessor, DataAccessor))
        self.assertFalse(isinstance(accessor, LofarAccessor))

    def test_injection(self):
        c = SafeConfigParser()
        c.read(default_header_inject_config)
        parset = parse_to_dict(c)['inject']

        tkp.inject.modify_fits_headers(parset, self.fixed_file, overwrite=True)
        fixed_fits = tkp.accessors.open(self.fixed_file)
        self.assertTrue(isinstance(fixed_fits, DataAccessor))
        self.assertTrue(isinstance(fixed_fits, LofarAccessor))
