import os

import unittest

from tkp import accessors
from tkp.accessors.aartfaaccasaimage import AartfaacCasaImage
from tkp.testutil.decorators import requires_data
from tkp.utility.coordinates import angsep
from tkp.testutil.data import DATAPATH


casatable = os.path.join(DATAPATH, 'accessors/aartfaac.table')


class TestAartfaacCasaImage(unittest.TestCase):
    @classmethod
    @requires_data(casatable)
    def setUpClass(cls):
        cls.accessor = AartfaacCasaImage(casatable)

    def test_casaimage(self):
        results = self.accessor.extract_metadata()
        sfimage = accessors.sourcefinder_image_from_accessor(self.accessor)

        known_bmaj, known_bmin, known_bpa = 4.4586, 4.458, 0
        bmaj, bmin, bpa = self.accessor.beam
        self.assertAlmostEqual(known_bmaj, bmaj, 2)
        self.assertAlmostEqual(known_bmin, bmin, 2)
        self.assertAlmostEqual(known_bpa, bpa, 2)

    def test_phase_centre(self):
        known_ra, known_decl = 118.859, 52.915
        self.assertAlmostEqual(self.accessor.centre_ra, known_ra, 2)
        self.assertAlmostEqual(self.accessor.centre_decl, known_decl, 2)

    def test_wcs(self):
        known_ra, known_dec = 335.90109, 44.654139
        known_x, known_y = 633.178, 457.342
        calc_x, calc_y = self.accessor.wcs.s2p([known_ra, known_dec])
        calc_ra, calc_dec = self.accessor.wcs.p2s([known_x, known_y])
        self.assertAlmostEqual(known_x, calc_x, 3)
        self.assertAlmostEqual(known_y, calc_y, 3)
        self.assertAlmostEqual(known_ra, calc_ra % 360, 3)
        self.assertAlmostEqual(known_dec, calc_dec, 3)

    def test_pix_scale(self):
        p1_sky = (self.accessor.centre_ra, self.accessor.centre_decl)
        p1_pix = self.accessor.wcs.s2p(p1_sky)

        pixel_sep = 10  # Along a single axis
        p2_pix = (p1_pix[0], p1_pix[1] + pixel_sep)
        p2_sky = self.accessor.wcs.p2s(p2_pix)

        coord_dist_deg = angsep(p1_sky[0], p1_sky[1], p2_sky[0], p2_sky[1]) / 3600.0
        pix_dist_deg = pixel_sep * self.accessor.pixelsize[1]

        # 6 decimal places => 1e-6*degree / 10pix => 1e-7*degree / 1pix
        #  => Approx 0.15 arcseconds drift across 512 pixels
        # (Probably OK).
        self.assertAlmostEqual(abs(coord_dist_deg), abs(pix_dist_deg), places=6)

