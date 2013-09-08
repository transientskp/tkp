import os
import tempfile
import shutil

import unittest2 as unittest

import tkp.bin.pyse
from tkp.accessors import FitsImage
from tkp.accessors import sourcefinder_image_from_accessor
from tkp.testutil.data import DATAPATH
from tkp.testutil import Mock


orig_fits_file = os.path.join(DATAPATH, 'pyse-test.fits')


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
    'fdr': False,
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

    def test_bailout(self):
        import sys
        old_exit = sys.exit
        sys.exit = Mock()
        tkp.bin.pyse.bailout("bad stuff")
        self.assertEqual(sys.exit.callcount, 1)
        sys.exit = old_exit

    def test_getbeam(self):
        self.assertEqual(
            tkp.bin.pyse.get_beam(1, 2, 3),
            (1.0, 2.0, 3.0)
        )
        self.assertEqual(
            tkp.bin.pyse.get_beam(1.0, 2.0, 3.0),
            (1.0, 2.0, 3.0)
        )
        self.assertEqual(
            tkp.bin.pyse.get_beam('a', 'b', 'c'),
            None
        )

    def test_get_sourcefinder_configuration(self):
        config = tkp.bin.pyse.get_sourcefinder_configuration(options)
        self.assertFalse(config["deblend"])
        self.assertTrue(config["residuals"])
        self.assertTrue(config["force_beam"])
        self.assertEqual(config['back_sizex'], options.grid)
        self.assertEqual(config['back_sizey'], options.grid)
        self.assertEqual(config['margin'], options.margin)
        self.assertEqual(config['radius'], options.radius)
        self.assertEqual(config['deblend_nthresh'], options.deblend_thresholds)

    def test_sourcefinder_gets_beam(self):
        old_get_beam = tkp.bin.pyse.get_beam
        tkp.bin.pyse.get_beam = Mock((options.bmaj, options.bmin, options.bpa))
        tkp.bin.pyse.run_sourcefinder([self.filename], options)
        self.assertEqual(tkp.bin.pyse.get_beam.callcount, 1)
        tkp.bin.pyse.get_beam = old_get_beam

    def test_sourcefinder_uses_detection_image(self):
        # Be sure that get_detection_labels() is called iff
        # options.detection_image is True.
        config = tkp.bin.pyse.get_sourcefinder_configuration(options)

        # First, get the correct answers for mocking
        detection_labels = tkp.bin.pyse.get_detection_labels(
            self.filename, options.detection, options.analysis,
            (options.bmaj, options.bmin, options.bpa), config
        )

        # Now insert our mocked function
        old_get_detection_labels = tkp.bin.pyse.get_detection_labels
        tkp.bin.pyse.get_detection_labels = Mock(detection_labels)

        # With default config, we should not run the function
        tkp.bin.pyse.run_sourcefinder([self.filename], options)
        self.assertEqual(tkp.bin.pyse.get_detection_labels.callcount, 0)

        # But if we set options.detection_image to True, we should
        options.detection_image = True
        tkp.bin.pyse.run_sourcefinder([self.filename], options)
        self.assertEqual(tkp.bin.pyse.get_detection_labels.callcount, 1)

        # Restore the old function
        tkp.bin.pyse.get_detection_labels = old_get_detection_labels
