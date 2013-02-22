import unittest2 as unittest
import os
import tkp.config

from tkp.utility.accessors.detection import isfits, islofarcasa, islofarhdf5, detect, iscasa
from tkp.utility.accessors.lofarcasaimage import LofarCasaImage
from tkp.utility.accessors.casaimage import CasaImage
from tkp.utility.accessors.lofarhdf5image import LofarHdf5Image
from tkp.utility.accessors.fitsimage import FitsImage
import tkp.utility.accessors
from tkp.testutil.decorators import requires_data

DATAPATH = tkp.config.config['test']['datapath']
lofarcasatable = os.path.join(DATAPATH, 'casatable/L55596_000TO009_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')
casatable = os.path.join(DATAPATH, 'L21641_SB098.restored.image')
fitsfile = os.path.join(DATAPATH, 'lofar15_12hr-corrected-I-mfs.fits')
hdf5file = os.path.join(DATAPATH, 'lofar.h5')
antennafile = os.path.join(DATAPATH, 'lofar/CS001-AntennaArrays.conf')

class TestAutodetect(unittest.TestCase):
    @requires_data(lofarcasatable)
    def test_islofarcasa(self):
        self.assertTrue(islofarcasa(lofarcasatable))
        self.assertTrue(iscasa(lofarcasatable))
        self.assertFalse(islofarhdf5(lofarcasatable))
        self.assertFalse(isfits(lofarcasatable))
        self.assertEqual(detect(lofarcasatable), LofarCasaImage)

    @requires_data(casatable)
    def test_iscasa(self):
        self.assertFalse(islofarcasa(casatable))
        self.assertTrue(iscasa(casatable))
        self.assertFalse(islofarhdf5(casatable))
        self.assertFalse(isfits(casatable))
        self.assertEqual(detect(casatable), CasaImage)

    @requires_data(hdf5file)
    def test_ishdf5(self):
        # TODO: disable this for now, since pyrap can't parse LOFAR hdf5
        #self.assertTrue(islofarhdf5(hdf5file))
        self.assertFalse(islofarcasa(hdf5file))
        self.assertFalse(isfits(hdf5file))
        self.assertFalse(iscasa(hdf5file))
        #self.assertEqual(detect(hdf5file), LofarHdf5Image)

    @requires_data(fitsfile)
    def test_isfits(self):
        self.assertTrue(isfits(fitsfile))
        self.assertFalse(islofarhdf5(fitsfile))
        self.assertFalse(islofarcasa(fitsfile))
        self.assertFalse(iscasa(fitsfile))
        self.assertEqual(detect(fitsfile), FitsImage)

    @requires_data(lofarcasatable, antennafile)
    def test_open(self):
        accessor = tkp.utility.accessors.open(lofarcasatable)
        self.assertEqual(accessor.__class__, LofarCasaImage)
        self.assertRaises(IOError, tkp.utility.accessors.open, antennafile)
        self.assertRaises(IOError, tkp.utility.accessors.open, 'doesntexists')
