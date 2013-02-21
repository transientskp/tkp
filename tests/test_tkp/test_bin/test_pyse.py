import os
import unittest
import tempfile
import shutil
import tkp.bin.pyse
import tkp.config
from tkp.utility.accessors import FitsImage
from tkp.utility.accessors import sourcefinder_image_from_accessor


data_path = tkp.config.config['test']['datapath']
orig_fits_file = os.path.join(data_path, 'L15_12h_const/observed-all.fits')


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
    'alpha': .1,
})


class TestPyse(unittest.TestCase):
    def __init__(self, *args):
        super(TestPyse, self).__init__(*args)
        temp_dir = tempfile.mkdtemp()
        self.filename = os.path.join(temp_dir, 'playground.fits')
        shutil.copy(orig_fits_file, self.filename)
        self.fits = FitsImage(self.filename)
        self.fits.beam = (.5, .5, .5)
        self.imagedata = sourcefinder_image_from_accessor(self.fits)
        self.sourcelist = self.imagedata.extract()

    def test_regions(self):
        tkp.bin.pyse.regions(self.sourcelist)

    def test_skymodel(self):
        tkp.bin.pyse.skymodel(self.sourcelist, ref_freq=73800000)

    def test_csv(self):
        tkp.bin.pyse.csv(self.sourcelist)

    def test_summary(self):
        tkp.bin.pyse.summary(self.filename, self.sourcelist)

    def test_handle_args(self):
        tkp.bin.pyse.handle_args()

    def test_writefites(self):
        t = tempfile.NamedTemporaryFile(delete=False)
        f = t.name
        data = self.fits.data
        tkp.bin.pyse.writefits(f, data, header={})

    def test_run_sourcefinder(self):
        # no options and files
        tkp.bin.pyse.run_sourcefinder([], options)
        # one file
        tkp.bin.pyse.run_sourcefinder([self.filename], options)
