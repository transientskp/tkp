# Tests for simulated LOFAR datasets.

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest

from utility.decorators import requires_data
from utility.decorators import requires_database
from utility.decorators import requires_module

import os
import tkp.config
from tkp.utility import accessors

DATAPATH = tkp.config.config['test']['datapath']

class FitsFile(unittest.TestCase):

    def setUp(self):
        pass

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testOpen(self):
        # Beam specified by user
        image = accessors.FitsFile(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'), beam=(54./3600, 54./3600, 0.))
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
        image = accessors.FitsFile(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
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
        image = accessors.FitsFile(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'),
                                   beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)

    @requires_module("pyrap")
    @requires_data(os.path.join(DATAPATH, 'CX3_peeled.image/'))
    def testSFImageFromAIPSpp(self):
        image = accessors.AIPSppImage(os.path.join(DATAPATH, 'CX3_peeled.image/'),
                                      beam=(54./3600, 54./3600, 0.))
        sfimage = accessors.sourcefinder_image_from_accessor(image)


class DataBaseImage(unittest.TestCase):

    @requires_database()
    @requires_data(os.path.join(DATAPATH, 'CX3_peeled.image/'))
    def testDBImageFromAccessor(self):
        from tkp.database.database import DataBase
        from tkp.database.dataset import DataSet
        image = accessors.AIPSppImage(os.path.join(DATAPATH, 'CX3_peeled.image/'),
                                      beam=(54./3600, 54./3600, 0.))
        database = DataBase()
        dataset = DataSet('dataset', database=database)
        dbimage = accessors.dbimage_from_accessor(dataset, image)


class FrequencyInformation(unittest.TestCase):
    
    @requires_database()
    @requires_data(os.path.join(DATAPATH, 'L21641_SB098.restored.image'))
    @requires_data(os.path.join(DATAPATH, 'VLSS.fits'))
    def testFreqinfo(self):
        from tkp.database.database import DataBase
        from tkp.database.dataset import DataSet
        database = DataBase()
        dataset = DataSet('dataset', database=database)
        image = accessors.AIPSppImage(
            os.path.join(DATAPATH, 'L21641_SB098.restored.image'))
        self.assertAlmostEqual(image.freqeff/1e6, 156.4453125)
        self.assertAlmostEqual(image.freqbw, 1.0)
        self.assertAlmostEqual(image.beam[0], 0.9)
        self.assertAlmostEqual(image.beam[1], 0.9)
        self.assertAlmostEqual(image.beam[2], 0.0)

        # image without frequency information
        image = accessors.FitsFile(os.path.join(DATAPATH, 'VLSS.fits'))
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
