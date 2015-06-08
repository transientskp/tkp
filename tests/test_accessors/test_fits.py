"""
Tests for simulated LOFAR datasets.
"""

import os
import unittest

from tkp.testutil.data import DATAPATH
from tkp import accessors
from tkp.accessors.fitsimage import FitsImage
from tkp.db.orm import DataSet
from tkp.db.database import Database
import tkp.db
from tkp.testutil.decorators import requires_data
from tkp.testutil.decorators import requires_database



class PyfitsFitsImage(unittest.TestCase):

    @requires_data(os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits'))
    @requires_data(os.path.join(DATAPATH, 'sourcefinder/simulations/correlated_noise.fits'))
    def testOpen(self):
        fits_file = os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits')
        image = FitsImage(fits_file, beam=(54./3600, 54./3600, 0.))
        self.assertAlmostEqual(image.beam[0], 0.225)
        self.assertAlmostEqual(image.beam[1], 0.225)
        self.assertAlmostEqual(image.beam[2], 0.)
        self.assertAlmostEqual(image.wcs.crval[0], 350.85)
        self.assertAlmostEqual(image.wcs.crval[1], 58.815)
        self.assertAlmostEqual(image.wcs.crpix[0], 1440.)
        self.assertAlmostEqual(image.wcs.crpix[1], 1440.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.03333333)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.03333333)
        self.assertEqual(image.wcs.ctype[0], 'RA---SIN')
        self.assertEqual(image.wcs.ctype[1], 'DEC--SIN')
        # Beam included in image
        fits_file = os.path.join(DATAPATH, 'sourcefinder/simulations/correlated_noise.fits')
        image = FitsImage(fits_file)
        self.assertAlmostEqual(image.beam[0], 2.7977999)
        self.assertAlmostEqual(image.beam[1], 2.3396999)
        self.assertAlmostEqual(image.beam[2], -0.869173967)
        self.assertAlmostEqual(image.wcs.crval[0], 266.363244382)
        self.assertAlmostEqual(image.wcs.crval[1], -29.9529359725)
        self.assertAlmostEqual(image.wcs.crpix[0], 127.)
        self.assertAlmostEqual(image.wcs.crpix[1], 128.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.003333333414)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.003333333414)
        self.assertEqual(image.wcs.ctype[0], 'RA---SIN')
        self.assertEqual(image.wcs.ctype[1], 'DEC--SIN')

    @requires_data(os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits'))
    def testSFImageFromFITS(self):
        fits_file = os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits')
        image = FitsImage(fits_file, beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)



class TestFitsImage(unittest.TestCase):

    @requires_data(os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits'))
    @requires_data(os.path.join(DATAPATH, 'sourcefinder/simulations/correlated_noise.fits'))
    def testOpen(self):
        # Beam specified by user
        fits_file = os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits')
        image = FitsImage(fits_file, beam=(54./3600, 54./3600, 0.))
        self.assertEqual(image.telescope, 'LOFAR20') #God knows why it's 'LOFAR20'
        self.assertAlmostEqual(image.beam[0], 0.225)
        self.assertAlmostEqual(image.beam[1], 0.225)
        self.assertAlmostEqual(image.beam[2], 0.)
        self.assertAlmostEqual(image.wcs.crval[0], 350.85)
        self.assertAlmostEqual(image.wcs.crval[1], 58.815)
        self.assertAlmostEqual(image.wcs.crpix[0], 1440.)
        self.assertAlmostEqual(image.wcs.crpix[1], 1440.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.03333333)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.03333333)
        self.assertEqual(image.wcs.ctype[0], 'RA---SIN')
        self.assertEqual(image.wcs.ctype[1], 'DEC--SIN')

        # Beam included in image
        image = FitsImage(os.path.join(DATAPATH, 'sourcefinder/simulations/correlated_noise.fits'))
        self.assertAlmostEqual(image.beam[0], 2.7977999)
        self.assertAlmostEqual(image.beam[1], 2.3396999)
        self.assertAlmostEqual(image.beam[2], -0.869173967)
        self.assertAlmostEqual(image.wcs.crval[0], 266.363244382)
        self.assertAlmostEqual(image.wcs.crval[1], -29.9529359725)
        self.assertAlmostEqual(image.wcs.crpix[0], 127.)
        self.assertAlmostEqual(image.wcs.crpix[1], 128.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.003333333414)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.003333333414)
        self.assertEqual(image.wcs.ctype[0], 'RA---SIN')
        self.assertEqual(image.wcs.ctype[1], 'DEC--SIN')

    @requires_data(os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits'))
    def testSFImageFromFITS(self):
        image = FitsImage(os.path.join(DATAPATH, 'sourcefinder/L15_12h_const/observed-all.fits'),
                                   beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)



class FrequencyInformation(unittest.TestCase):
    @requires_data(os.path.join(DATAPATH, 'accessors/missing_metadata.fits'))
    def testFreqinfo(self):
        # Frequency information is required by the data accessor.
        self.assertRaises(TypeError, FitsImage,
                          os.path.join(DATAPATH, 'accessors/missing_metadata.fits'))


if __name__ == '__main__':
    unittest.main()
