import os
import unittest
from optparse import OptionParser
from tempfile import NamedTemporaryFile
import tkp.bin.pyse
import tkp.config
from tkp.utility.accessors import FitsImage
from tkp.utility.accessors import sourcefinder_image_from_accessor

data_path = tkp.config.config['test']['datapath']
fits_file = os.path.join(data_path, 'L15_12h_const/observed-all.fits')


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

options = AttributeDict({
    'grid': 0,
    'margin': 0,
    'radius': 0,
    'deblend': False,
    'deblend_thresholds': 32,
    'residuals': False,
    'islands': False,
    'fdr': False,
    'bmaj': 0.5,
    'bmin': 0.5,
    'bpa': 0.5,
    'detection': 0,
    'options.analysis': 0,
})

class TestPyse(unittest.TestCase):
    def __init__(self, *args):
        super(TestPyse, self).__init__(*args)
        self.fits = FitsImage(fits_file)
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
        tkp.bin.pyse.summary(fits_file, self.sourcelist)

    def test_handle_args(self):
        tkp.bin.pyse.handle_args()

    def test_writefites(self):
        tempfile = NamedTemporaryFile(delete=False)
        filename = tempfile.name
        data = self.fits.data
        tkp.bin.pyse.writefits(filename, data, header={})

    def test_run_sourcefinder(self):
        # no options and files
        tkp.bin.pyse.run_sourcefinder([], options)
        # one file
        tkp.bin.pyse.run_sourcefinder([fits_file], options)
