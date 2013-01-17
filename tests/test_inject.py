import unittest
import os
import tempfile
import shutil
import tkp
import tkp.utility.accessors
import trap.inject

DATAPATH = tkp.config.config['test']['datapath']
fits_file = os.path.join(DATAPATH, 'missingheaders.fits')



class TestInject(unittest.TestCase):
    def __init__(self, *args):
        super(TestInject, self).__init__(*args)
        temp_dir = tempfile.mkdtemp()
        self.fixed_file = os.path.join(temp_dir, 'fixed.fits')
        shutil.copy(fits_file, self.fixed_file)

    def test_no_injection(self):
        # stuff should be missing here

        missing_fits = tkp.utility.accessors.open(fits_file)
        self.assertTrue(missing_fits.not_set() != [])

    def test_injection(self):
        parset = {} # TODO: set overwrite vars here
        trap.inject.modify_headers(parset, self.fixed_file)
        fixed_fits = tkp.utility.accessors.open(fits_file)
        self.assertTrue(fixed_fits.not_set() == [])