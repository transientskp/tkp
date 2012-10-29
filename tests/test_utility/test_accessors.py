# Tests for simulated LOFAR datasets.

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
import pyfits
import h5py
import tkp.config
from tkp.utility import accessors
from tkp.utility.accessors.lofarimage import LofarImage
from tkp.utility.accessors.fitsimage import FITSImage
from tkp.database import DataSet
from tkp.database import DataBase
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data
from decorators import requires_database

DATAPATH = tkp.config.config['test']['datapath']

class PyfitsFITSImage(unittest.TestCase):

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    def testOpen(self):
        hdu = pyfits.open(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'), mode="readonly")
        image = accessors.FITSImage(hdu, beam=(54./3600, 54./3600, 0.))
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
        image = accessors.FITSImage(hdu)
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
        image = accessors.FITSImage(hdu, beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)



class TestFITSImage(unittest.TestCase):

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    @requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
    def testOpen(self):
        # Beam specified by user
        image = accessors.FITSImage(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'), beam=(54./3600, 54./3600, 0.))
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
        image = accessors.FITSImage(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
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
        image = accessors.FITSImage(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'),
                                   beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)


class DataBaseImage(unittest.TestCase):
    """TO DO: split this into an accessor test and a database test.
                Move the database part to the database unit-tests"""
    @requires_database()
    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testDBImageFromAccessor(self):
        import tkp.database.database 

        image = FITSImage(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'),
                                      beam=(54./3600, 54./3600, 0.))
        
        database = tkp.database.database.DataBase()
        dataset = DataSet(data={'description': 'Accessor test'}, database=database)
        dbimage = accessors.dbimage_from_accessor(dataset, image)


class FrequencyInformation(unittest.TestCase):
    """TO DO: split this into an accessor test and a database test.
                Move the database part to the database unit-tests"""
    @requires_database()
    @requires_data(os.path.join(DATAPATH, 'L21641_SB098.restored.image'))
    @requires_data(os.path.join(DATAPATH, 'VLSS.fits'))
    def testFreqinfo(self):
        database = DataBase()
        dataset = DataSet(data={'description': 'dataset'}, database=database)
        image = accessors.AIPSppImage(
            os.path.join(DATAPATH, 'L21641_SB098.restored.image'))
        self.assertAlmostEqual(image.freqeff/1e6, 156.4453125)
        self.assertAlmostEqual(image.freqbw, 1.0)
        self.assertAlmostEqual(image.beam[0], 0.9)
        self.assertAlmostEqual(image.beam[1], 0.9)
        self.assertAlmostEqual(image.beam[2], 0.0)

        # image without frequency information
        image = accessors.FITSImage(os.path.join(DATAPATH, 'VLSS.fits'))
        # The database requires frequency information
        self.assertRaises(ValueError, accessors.dbimage_from_accessor,
                          dataset, image)
        # But the sourcefinder does not need frequency information
        self.assertListEqual(
            list(accessors.sourcefinder_image_from_accessor(image).data.shape),
            [2048, 2048])
        database.close()


lofar_file = os.path.join(DATAPATH, 'lofar.h5')
@requires_data(lofar_file)
@unittest.skip # disable for now since not working :)
class TestLofarFile(unittest.TestCase):

    def testOpen(self):
        file_handler = h5py.File(lofar_file,'r')
        image = LofarImage(file_handler) #, beam=(54./3600, 54./3600, 0.))


        file_handler = h5py.File(lofar_file,'r')
        image = LofarImage(file_handler)
        sfimage = accessors.sourcefinder_image_from_accessor(image)
        pass

if __name__ == '__main__':
    unittest.main()
