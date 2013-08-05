import os
import tempfile
import shutil

import unittest2 as unittest

import tkp.bin.pyse
from tkp.accessors import FitsImage
from tkp.accessors import sourcefinder_image_from_accessor
from tkp.testutil.data import DATAPATH


orig_fits_file = os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits')


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


options = AttributeDict({
    'grid': 100,
    'margin': 0,
    'radius': 0,
    'deblend': False,
    'deblend_thresholds': 32,
    'residuals': True,
    'islands': True,
    'fdr': True,
    'bmaj': 0.5,
    'bmin': 0.5,
    'bpa': 0.5,
    'detection': 5,
    'analysis': 5,
    'regions': True,
    'rmsmap': True,
    'sigmap': True,
    'skymodel': True,
    'csv': True,
    'force_beam': True,
    'alpha': .1,
    'detection_image': False
})


class TestPyse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.start_dir = os.getcwd()
        os.chdir(cls.temp_dir)
        cls.filename = os.path.join(cls.temp_dir, 'playground.fits')
        shutil.copy(orig_fits_file, cls.filename)
        cls.fits = FitsImage(cls.filename, beam=(.5, .5, .5))
        cls.imagedata = sourcefinder_image_from_accessor(cls.fits)
        cls.sourcelist = cls.imagedata.extract()

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.start_dir)
        shutil.rmtree(cls.temp_dir)

    def test_regions(self):
        tkp.bin.pyse.regions(self.sourcelist)

    def test_skymodel(self):
        tkp.bin.pyse.skymodel(self.sourcelist, ref_freq=73800000)

    def test_csv(self):
        tkp.bin.pyse.csv(self.sourcelist)

    def test_summary(self):
        tkp.bin.pyse.summary(self.filename, self.sourcelist)

    @unittest.skip("TODO: disabled since clashes with nosetest arguments.")
    def test_handle_args(self):
        tkp.bin.pyse.handle_args()

    def test_writefites(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        data = self.fits.data
        tkp.bin.pyse.writefits(temp_file.name, data, header={})
        os.unlink(temp_file.name)

    def test_run_sourcefinder(self):
        # no options and files
        tkp.bin.pyse.run_sourcefinder([], options)
        # one file
        tkp.bin.pyse.run_sourcefinder([self.filename], options)
