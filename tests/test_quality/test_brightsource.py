import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
from math import degrees
from tkp.testutil.decorators import requires_data
import tkp.quality.brightsource
import tkp.utility.accessors
import tkp.config

DATAPATH = tkp.config.config['test']['datapath']
testimage = os.path.join(DATAPATH,
    'casatable/L55614_020TO029_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

class TestBrightsource(unittest.TestCase):
    @requires_data(testimage)
    def test_brightsource(self):
        image = tkp.utility.accessors.open(testimage)

        # this image is not near any bright sources
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertFalse(result)

        # there is nothing bright here
        image.centre_ra = 90
        image.centre_decl = 0
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertFalse(result)

        # this is near the sun
        image.centre_ra = 0
        image.centre_decl = 0
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertTrue(result)

        # this is near CasA
        image.centre_ra = degrees(6.123487680622104)
        image.centre_decl = degrees(1.0265153995604648)
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertTrue(result)
