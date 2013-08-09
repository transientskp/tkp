import unittest
import os
import tempfile
import shutil
import tkp
import tkp.accessors
import tkp.inject
from tkp.testutil.data import DATAPATH
import tkp.utility.parset
from tkp.testutil.data import default_parset_paths

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
        # stuff should be missing here
        self.assertRaises(KeyError, tkp.accessors.open, fits_file)

    def test_injection(self):
        with open(default_parset_paths['inject.parset']) as f:
            parset = tkp.utility.parset.read_config_section(f, 'inject')

        tkp.inject.modify_fits_headers(parset, self.fixed_file, overwrite=True)
        fixed_fits = tkp.accessors.open(self.fixed_file)
