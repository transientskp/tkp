from math import degrees
from casacore.measures import measures

import unittest
import datetime

import tkp.quality.brightsource
import tkp.accessors
from tkp.testutil.mock import SyntheticImage, make_wcs

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


#class TestBrightsource(unittest.TestCase):
#    def test_brightsource(self):
#        wcs = make_wcs(crval=(212.83583333333334, 52.2025))
#        image = SyntheticImage(
#            wcs = wcs,
#            tau_time=58141509,
#            taustart_ts=datetime.datetime(2012, 4, 6, 3, 42, 1),
#            freq_eff=128613281.25,
#            freq_bw=1940917.96875,
#            beam= (1.9211971282958984, 1.7578132629394532, 1.503223674140207),
#        )
#
#        # this image is not near any bright sources
#        result = tkp.quality.brightsource.is_bright_source_near(image)
#        self.assertFalse(result)
#
#        # there is nothing bright here
#        image.centre_ra = 90
#        image.centre_decl = 0
#        result = tkp.quality.brightsource.is_bright_source_near(image)
#        self.assertFalse(result)
#
#        # this is near the sun
#        image.centre_ra = 0
#        image.centre_decl = 0
#        result = tkp.quality.brightsource.is_bright_source_near(image)
#        self.assertTrue(result)
#
#        # this is near CasA
#        image._centre_ra = degrees(6.123487680622104)
#        image._centre_decl = degrees(1.0265153995604648)
#        result = tkp.quality.brightsource.is_bright_source_near(image)
#        self.assertTrue(result)
