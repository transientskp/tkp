import unittest
import os
import tempfile
import shutil
from configparser import SafeConfigParser
import tkp
import tkp.accessors
import tkp.inject
from tkp.testutil.data import DATAPATH
from tkp.config import parse_to_dict
from tkp.testutil.data import default_header_inject_config
from tkp.accessors.lofaraccessor import LofarAccessor
from tkp.accessors.dataaccessor import DataAccessor

fits_file = os.path.join(DATAPATH, 'inject/missingheaders.fits')
lofar_casatable = os.path.join(DATAPATH, 'casatable/L55596_000TO009_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

class TestFitsInject(unittest.TestCase):
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
        # Without injection the file cannot be opened because the frequency
        # isn't specified.
        self.assertRaises(TypeError, tkp.accessors.open, fits_file)

    def test_injection(self):
        c = SafeConfigParser()
        c.read(default_header_inject_config)
        parset = parse_to_dict(c)['inject']

        tkp.inject.modify_fits_headers(parset, self.fixed_file, overwrite=True)
        fixed_fits = tkp.accessors.open(self.fixed_file)
        self.assertTrue(isinstance(fixed_fits, DataAccessor))
        self.assertTrue(isinstance(fixed_fits, LofarAccessor))

class TestLofarCasaInject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_dir = os.getcwd()
        cls.temp_dir = tempfile.mkdtemp()
        cls.fixed_ms = os.path.join(cls.temp_dir, 'fixed.ms')
        shutil.copytree(lofar_casatable, cls.fixed_ms)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.start_dir)
        shutil.rmtree(cls.temp_dir)

    def test_no_injection(self):
        original_ms = tkp.accessors.open(lofar_casatable)
        self.assertAlmostEqual(original_ms.tau_time, 58141509)

    def test_tau_time_injection(self):
        inject_dict = {'tau_time' : 42 }
        tkp.inject.modify_lofarcasa_tau_time(inject_dict, self.fixed_ms)
        fixed_ms = tkp.accessors.open(self.fixed_ms)
        self.assertTrue(isinstance(fixed_ms, DataAccessor))
        self.assertTrue(isinstance(fixed_ms, LofarAccessor))
        self.assertAlmostEqual(fixed_ms.tau_time, inject_dict['tau_time'])

    def test_other_keyword_injection(self):
        inject_dict = dict(ncore = 41)
        with self.assertRaises(ValueError):
            tkp.inject.modify_lofarcasa_tau_time(inject_dict, self.fixed_ms)
