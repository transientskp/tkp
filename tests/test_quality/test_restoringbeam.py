import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import requires_data

from tkp.utility import accessors
import tkp.quality.restoringbeam

import tkp.lofar.noise
import tkp.config
import tkp.lofar.antennaarrays

DATAPATH = tkp.config.config['test']['datapath']
fits_file = os.path.join(DATAPATH, 'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits')

@requires_data(fits_file)
class TestRestoringBeam(unittest.TestCase):
    def test_header(self):
        image = accessors.FitsFile(fits_file, plane=0)
        bmaj, bmin, cellsize = tkp.quality.restoringbeam.parse_fits(image)
        #self.assertFalse(tkp.quality.restoringbeam.oversampled(bmaj, bmin, cellsize))
        #self.assertFalse(tkp.quality.restoringbeam.undersampled(bmaj, bmin, cellsize))


if __name__ == '__main__':
    unittest.main()
