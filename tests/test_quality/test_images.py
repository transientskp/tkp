__author__ = 'gijs'

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
from tkp.utility import accessors
from tkp.sourcefinder import image
import tkp.config

# relative imports suck. This way we are sure python tries to load the module from the parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data

DATAPATH = tkp.config.config['test']['datapath']
NUMBER_INSERTED = float(3969)


@unittest.skipIf(not eval(tkp.config.config['test']['long']), "not runnig prolonged test suite")
@requires_data(os.path.join(DATAPATH, 'UNCORRELATED_NOISE.FITS'))
@requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
@requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
class test_maps(unittest.TestCase):
    def setUp(self):
        uncorr_map = accessors.FitsFile(os.path.join(DATAPATH, 'UNCORRELATED_NOISE.FITS'))
        corr_map = accessors.FitsFile(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
        map_with_sources = accessors.FitsFile(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))

        uncorr_image = image.ImageData(uncorr_map.data, uncorr_map.beam, uncorr_map.wcs)
        corr_image = image.ImageData(corr_map.data, uncorr_map.beam, uncorr_map.wcs)
        image_with_sources = image.ImageData(map_with_sources.data, map_with_sources.beam, map_with_sources.wcs)

        self.number_detections_uncorr = len(uncorr_image.fd_extract())
        self.number_detections_corr = len(corr_image.fd_extract())
        self.number_alpha_10pc = len(image_with_sources.fd_extract(alpha=0.1))
        self.number_alpha_1pc = len(image_with_sources.fd_extract(alpha=0.01))
        self.number_alpha_point1pc = len(image_with_sources.fd_extract(alpha=0.001))


    def testNumSources(self):
        self.assertEqual(self.number_detections_uncorr, 0)
        self.assertEqual(self.number_detections_corr, 0)

        self.assertTrue((self.number_alpha_10pc-NUMBER_INSERTED)/NUMBER_INSERTED < 0.1)
        self.assertTrue((self.number_alpha_1pc-NUMBER_INSERTED)/NUMBER_INSERTED < 0.01)
        self.assertTrue((self.number_alpha_point1pc-NUMBER_INSERTED)/NUMBER_INSERTED < 0.001)


if __name__ == '__main__':
    unittest.main()
