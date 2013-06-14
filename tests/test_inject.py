import unittest
import os
import tempfile
import shutil
import tkp
import tkp.utility.accessors
import tkp.inject
from tkp.testutil.data import DATAPATH
import tkp.utility.parset
from tkp.testutil import default_parset_paths

fits_file = os.path.join(DATAPATH, 'missingheaders.fits')

class TestInject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp_dir = tempfile.mkdtemp()
        cls.fixed_file = os.path.join(temp_dir, 'fixed.fits')
        shutil.copy(fits_file, cls.fixed_file)

    def test_no_injection(self):
        # stuff should be missing here

        missing_fits = tkp.utility.accessors.open(fits_file)
        self.assertTrue(missing_fits.not_set() != [])

    def test_injection(self):
        with open(default_parset_paths['inject.parset']) as f:
            parset = tkp.utility.parset.read_config_section(f, 'inject')

        tkp.inject.modify_fits_headers(parset, self.fixed_file)
        fixed_fits = tkp.utility.accessors.open(self.fixed_file)
        self.assertTrue(fixed_fits.not_set() == [])
