import unittest2 as unittest
from tkp.utility.coordinates import WCS
from tkp.sourcefinder.extract import Detection
from tkp.utility.uncertain import Uncertain
from tkp.sourcefinder.extract import ParamSet


class TestPositionErrors(unittest.TestCase):
    def setUp(self):
       # We will create a WCS object for an image centred on the north
       # celestial pole.
       class DummyImage(object): pass
       self.dummy_image = DummyImage()
       self.dummy_image.wcs = WCS()
       self.dummy_image.wcs.cdelt = (-0.009722222222222, 0.009722222222222)
       self.dummy_image.wcs.crota = (0.0, 0.0)
       self.dummy_image.wcs.crpix = (1025, 1025) # Pixel position of reference
       self.dummy_image.wcs.crval = (15.0, 90.0) # Celestial position of reference
       self.dummy_image.wcs.ctype = ('RA---SIN', 'DEC--SIN')
       self.dummy_image.wcs.cunit = ('deg', 'deg')
       self.dummy_image.wcs.wcsset()

    def test_ra_error_scaling(self):
        # Demonstrate that RA errors scale with declination.
        # See HipChat discussion of 2013-08-28.
        # Values of all parameters are dummies except for the pixel position.
        p = ParamSet()
        p.sig = 1
        p.values = {
            'peak': Uncertain(1, 0),
            'flux': Uncertain(1, 0),
            'semimajor': Uncertain(10, 1),
            'semiminor': Uncertain(10, 1),
            'theta': Uncertain(0, 1),
            'semimaj_deconv': Uncertain(10, 1),
            'semimin_deconv': Uncertain(10, 1),
            'theta_deconv': Uncertain(10, 1)
        }

        # First, construct a source at the NCP
        p.values['xbar'] = Uncertain(1025, 1)
        p.values['ybar'] = Uncertain(1025, 1)
        d_ncp = Detection(p, self.dummy_image)

        # Then construct a source somewhere away from the NCP
        p.values['xbar'] = Uncertain(125, 1)
        p.values['ybar'] = Uncertain(125, 1)
        d_not_ncp = Detection(p, self.dummy_image)

        # The error at higher declination must be greater
        self.assertGreater(d_ncp.ra.error, d_not_ncp.ra.error)
        self.assertGreater(d_ncp.dec.value, d_not_ncp.dec.value)
