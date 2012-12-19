# Tests for simulated LOFAR datasets.

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import pyfits
import tkp.config
from tkp.utility import accessors
from tkp.utility.accessors.casaimage import CasaImage
from tkp.utility.accessors.fitsimage import FitsImage
from tkp.database import DataSet
from tkp.database import DataBase
from tkp.testutil.decorators import requires_data
from tkp.testutil.decorators import requires_database

DATAPATH = tkp.config.config['test']['datapath']

class PyfitsFitsImage(unittest.TestCase):

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    def testOpen(self):
        hdu = pyfits.open(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'), mode="readonly")
        image = FitsImage(hdu, beam=(54./3600, 54./3600, 0.))
        self.assertAlmostEqual(image.beam[0], 0.225)
        self.assertAlmostEqual(image.beam[1], 0.225)
        self.assertAlmostEqual(image.beam[2], 0.)
        self.assertAlmostEqual(image.wcs.crval[0], 350.85)
        self.assertAlmostEqual(image.wcs.crval[1], 58.815)
        self.assertAlmostEqual(image.wcs.crpix[0], 1441.)
        self.assertAlmostEqual(image.wcs.crpix[1], 1441.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.03333333)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.03333333)
        self.assertTupleEqual(image.wcs.ctype, ('RA---SIN', 'DEC--SIN'))
        # Beam included in image
        hdu = pyfits.open(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'), mode="readonly")
        image = FitsImage(hdu)
        self.assertAlmostEqual(image.beam[0], 2.7977999)
        self.assertAlmostEqual(image.beam[1], 2.3396999)
        self.assertAlmostEqual(image.beam[2], -0.869173967)
        self.assertAlmostEqual(image.wcs.crval[0], 266.363244382)
        self.assertAlmostEqual(image.wcs.crval[1], -29.9529359725)
        self.assertAlmostEqual(image.wcs.crpix[0], 128.)
        self.assertAlmostEqual(image.wcs.crpix[1], 129.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.003333333414)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.003333333414)
        self.assertTupleEqual(image.wcs.ctype, ('RA---SIN', 'DEC--SIN'))

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testSFImageFromFITS(self):
        hdu = pyfits.open(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
        image = FitsImage(hdu, beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)



class TestFitsImage(unittest.TestCase):

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    def testOpen(self):
        # Beam specified by user
        image = FitsImage(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'), beam=(54./3600, 54./3600, 0.))
        self.assertAlmostEqual(image.beam[0], 0.225)
        self.assertAlmostEqual(image.beam[1], 0.225)
        self.assertAlmostEqual(image.beam[2], 0.)
        self.assertAlmostEqual(image.wcs.crval[0], 350.85)
        self.assertAlmostEqual(image.wcs.crval[1], 58.815)
        self.assertAlmostEqual(image.wcs.crpix[0], 1441.)
        self.assertAlmostEqual(image.wcs.crpix[1], 1441.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.03333333)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.03333333)
        self.assertTupleEqual(image.wcs.ctype, ('RA---SIN', 'DEC--SIN'))
        # Beam included in image
        image = FitsImage(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
        self.assertAlmostEqual(image.beam[0], 2.7977999)
        self.assertAlmostEqual(image.beam[1], 2.3396999)
        self.assertAlmostEqual(image.beam[2], -0.869173967)
        self.assertAlmostEqual(image.wcs.crval[0], 266.363244382)
        self.assertAlmostEqual(image.wcs.crval[1], -29.9529359725)
        self.assertAlmostEqual(image.wcs.crpix[0], 128.)
        self.assertAlmostEqual(image.wcs.crpix[1], 129.)
        self.assertAlmostEqual(image.wcs.cdelt[0], -0.003333333414)
        self.assertAlmostEqual(image.wcs.cdelt[1], 0.003333333414)
        self.assertTupleEqual(image.wcs.ctype, ('RA---SIN', 'DEC--SIN'))

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testSFImageFromFITS(self):
        image = FitsImage(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'),
                                   beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)


class DataBaseImage(unittest.TestCase):
    """TO DO: split this into an accessor test and a database test.
                Move the database part to the database unit-tests"""
    @requires_database()
    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testDBImageFromAccessor(self):
        import tkp.database.database 

        image = FitsImage(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'),
                                      beam=(54./3600, 54./3600, 0.))

        database = tkp.database.database.DataBase()
        dataset = DataSet(data={'description': 'Accessor test'}, database=database)
        dbimage = accessors.dbimage_from_accessor(dataset, image)


class FrequencyInformation(unittest.TestCase):
    """TO DO: split this into an accessor test and a database test.
                Move the database part to the database unit-tests"""
    @requires_database()
    @requires_data(os.path.join(DATAPATH, 'VLSS.fits'))
    def testFreqinfo(self):
        database = DataBase()
        dataset = DataSet(data={'description': 'dataset'}, database=database)

        # image without frequency information
        image = FitsImage(os.path.join(DATAPATH, 'VLSS.fits'))
        # The database requires frequency information
        self.assertRaises(ValueError, accessors.dbimage_from_accessor,
                          dataset, image)
        # But the sourcefinder does not need frequency information
        self.assertListEqual(
            list(accessors.sourcefinder_image_from_accessor(image).data.shape),
            [2048, 2048])
        database.close()

if __name__ == '__main__':
    unittest.main()
