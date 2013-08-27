import os
from math import degrees
from pyrap.measures import measures

import unittest2 as unittest

from tkp.testutil.decorators import requires_data
import tkp.quality.brightsource
import tkp.accessors
from tkp.testutil.data import DATAPATH

testimage = os.path.join(DATAPATH,
    'casatable/L55614_020TO029_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

class TestEphemeris(unittest.TestCase):
    # Tests whether we can correctly identify that an ephemeris is invalid.
    # I don't think it's possible to test that we can correctly identify a
    # valid ephemeris, because we can't be sure that the user actually has one
    # on disk (unless we ship one with the test case, but I don't think it's
    # worth it.)
    def test_invalid_ephemeris(self):
        dm = measures()
        # No(?) ephemeris we're likely to come across is valid at MJD 0.
        dm.do_frame(dm.epoch("UTC", "0.0d"))
        self.assertFalse(tkp.quality.brightsource.check_for_valid_ephemeris(dm))


class TestBrightsource(unittest.TestCase):
    @requires_data(testimage)
    def test_brightsource(self):
        image = tkp.accessors.open(testimage)

        # this image is not near any bright sources
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertFalse(result)

        # there is nothing bright here
        image._centre_ra = 90
        image._centre_decl = 0
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertFalse(result)

        # this is near the sun
        image._centre_ra = 0
        image._centre_decl = 0
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertTrue(result)

        # this is near CasA
        image._centre_ra = degrees(6.123487680622104)
        image._centre_decl = degrees(1.0265153995604648)
        result = tkp.quality.brightsource.is_bright_source_near(image)
        self.assertTrue(result)
