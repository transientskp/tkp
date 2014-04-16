import unittest

import math
from tkp.utility.coordinates import WCS
from tkp.sourcefinder.extract import Detection
from tkp.utility.uncertain import Uncertain
from tkp.sourcefinder.extract import ParamSet
from tkp.sourcefinder.utils import get_error_radius

class DummyImage(object): pass

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

class TestPositionErrors(unittest.TestCase):
    def setUp(self):
       # An image pointing at the north celestial pole
       self.ncp_image = DummyImage()
       self.ncp_image.wcs = WCS()
       self.ncp_image.wcs.cdelt = (-0.009722222222222, 0.009722222222222)
       self.ncp_image.wcs.crota = (0.0, 0.0)
       self.ncp_image.wcs.crpix = (1025, 1025) # Pixel position of reference
       self.ncp_image.wcs.crval = (15.0, 90.0) # Celestial position of reference
       self.ncp_image.wcs.ctype = ('RA---SIN', 'DEC--SIN')
       self.ncp_image.wcs.cunit = ('deg', 'deg')
       self.ncp_image.wcs.wcsset()

       # And an otherwise identical one at the equator
       self.equator_image = DummyImage()
       self.equator_image.wcs = WCS()
       self.equator_image.wcs.cdelt = self.ncp_image.wcs.cdelt
       self.equator_image.wcs.crota = self.ncp_image.wcs.crota
       self.equator_image.wcs.crpix = self.ncp_image.wcs.crpix
       self.equator_image.wcs.crval = (15.0, 0.0) # Celestial position of reference
       self.equator_image.wcs.ctype = self.ncp_image.wcs.ctype
       self.equator_image.wcs.cunit = self.ncp_image.wcs.cunit
       self.equator_image.wcs.wcsset()

    def test_ra_error_scaling(self):
        # Demonstrate that RA errors scale with declination.
        # See HipChat discussion of 2013-08-28.
        # Values of all parameters are dummies except for the pixel position.
        # First, construct a source at the NCP
        p.values['xbar'] = Uncertain(1025, 1)
        p.values['ybar'] = Uncertain(1025, 1)
        d_ncp = Detection(p, self.ncp_image)

        # Then construct a source somewhere away from the NCP
        p.values['xbar'] = Uncertain(125, 1)
        p.values['ybar'] = Uncertain(125, 1)
        d_not_ncp = Detection(p, self.ncp_image)

        # One source is at higher declination
        self.assertGreater(d_ncp.dec.value, d_not_ncp.dec.value)

        # The RA error at higher declination must be greater
        self.assertGreater(d_ncp.ra.error, d_not_ncp.ra.error)

    def test_error_radius_value(self):
        # Demonstrate that we calculate the expected value for the error
        # radius
        p.values['xbar'] = Uncertain(1025, 1)
        p.values['ybar'] = Uncertain(1025, 1)
        d_ncp = Detection(p, self.ncp_image)

        # cdelt gives the per-pixel increment along the axis in degrees
        # Detection.error_radius is in arcsec
        expected_error_radius = math.sqrt(
            (p.values['xbar'].error * self.ncp_image.wcs.cdelt[0] * 3600)**2 +
            (p.values['ybar'].error * self.ncp_image.wcs.cdelt[1] * 3600)**2
        )

        self.assertAlmostEqual(d_ncp.error_radius, expected_error_radius, 6)

    def test_error_radius_with_dec(self):
        p.values['xbar'] = Uncertain(1025, 1)
        p.values['ybar'] = Uncertain(1025, 1)
        d_ncp = Detection(p, self.ncp_image)
        d_equator = Detection(p, self.equator_image)
        self.assertEqual(d_ncp.error_radius, d_equator.error_radius)
