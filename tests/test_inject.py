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
        parset = {
            'taustart_ts': '2007-07-20T14:18:09.909001',
            'freq_eff': 1000000.0,
            'freq_bw': 50.0,
            'tau_time': 1000.0,
            'antenna_set': 'HBA',
            'subbands': 40,
            'channels': 40,
            'ncore': 1000,
            'nremote': 10000,
            'nintl': 3,
            'position': 10,
            'subbandwidth': 10,
            'bmaj': 0.4,
            'bmin': 0.4,
            'bpa': 0.4,
        }

        trap.inject.modify_fits_headers(parset, self.fixed_file)
        fixed_fits = tkp.utility.accessors.open(self.fixed_file)
        self.assertTrue(fixed_fits.not_set() == [])
