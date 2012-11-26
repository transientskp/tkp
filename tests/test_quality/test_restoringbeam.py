import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
from tkp.testutil.decorators import requires_data
from tkp.utility import accessors
import tkp.quality.restoringbeam
import tkp.lofar.beam
import tkp.config

DATAPATH = tkp.config.config['test']['datapath']
fits_file = os.path.join(DATAPATH,
    'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits')

@requires_data(fits_file)
class TestRestoringBeam(unittest.TestCase):
    def test_header(self):
        image = accessors.FitsFile(fits_file, plane=0)
        (semimaj, semimin, theta) = image.beam
        self.assertFalse(tkp.quality.beam_invalid(semimaj, semimin))

        # TODO: this is for FOV calculation and checking
        #data = tkp.quality.restoringbeam.parse_fits(image)
        #frequency = image.freqeff
        #wavelength = scipy.constants.c/frequency
        #d = 32.25
        #fwhm = tkp.lofar.beam.fwhm(wavelength, d)
        #fov = tkp.lofar.beam.fov(fwhm)


if __name__ == '__main__':
    unittest.main()
