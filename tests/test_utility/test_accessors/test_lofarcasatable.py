import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
from tkp.utility import accessors
from tkp.utility.accessors.lofarcasaimage import LofarCasaImage
from tkp.utility.accessors.dataaccessor import extract_metadata
import tkp.config
from tkp.testutil.decorators import requires_data
from tkp.utility.coordinates import angsep


DATAPATH = tkp.config.config['test']['datapath']

casatable =  os.path.join(DATAPATH, 'casatable/L55596_000TO009_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

@requires_data(casatable)
class TestLofarCasaImage(unittest.TestCase):
    def test_casaimage(self):
        accessor = LofarCasaImage(casatable)
        results = extract_metadata(accessor)
        sfimage = accessors.sourcefinder_image_from_accessor(accessor)

    def test_parse_beam(self):
        accessor = LofarCasaImage(casatable)
        known_bmaj, known_bmin, known_bpa = 2.64, 1.85, 1.11
        bmaj, bmin, bpa = accessor.beam
        self.assertAlmostEqual(known_bmaj, bmaj, 2)
        self.assertAlmostEqual(known_bmin, bmin, 2)
        self.assertAlmostEqual(known_bpa, bpa, 2)

    def test_phase_centre(self):
        accessor = LofarCasaImage(casatable)
        known_ra, known_decl = 212.836, 52.203
        self.assertAlmostEqual(accessor.centre_ra, known_ra, 2)
        self.assertAlmostEqual(accessor.centre_decl, known_decl, 2)

    def test_wcs(self):
        accessor = LofarCasaImage(casatable)
        known_ra, known_dec = 212.82677, 52.2025
        known_x, known_y = 256.5, 256.0
        calc_x, calc_y = accessor.wcs.s2p([known_ra, known_dec])
        calc_ra, calc_dec = accessor.wcs.p2s([known_x, known_y])

        self.assertAlmostEqual(known_ra, calc_ra, 3)
        self.assertAlmostEqual(known_dec, calc_dec, 3)
        self.assertAlmostEqual(known_x, calc_x, 3)
        self.assertAlmostEqual(known_y, calc_y, 3)

    def test_pix_scale(self):
        accessor = LofarCasaImage(casatable)
        p1_sky = (accessor.centre_ra, accessor.centre_decl)
        p1_pix = accessor.wcs.s2p(p1_sky)

        pixel_sep = 10 #Along a single axis 
        p2_pix = (p1_pix[0], p1_pix[1] + pixel_sep)
        p2_sky = accessor.wcs.p2s(p2_pix)

        coord_dist_deg = angsep(p1_sky[0], p1_sky[1], p2_sky[0], p2_sky[1]) / 3600.0
        pix_dist_deg = pixel_sep * accessor.pixel_scale

        #6 decimal places => 1e-6*degree / 10pix => 1e-7*degree / 1pix 
        #  => Approx 0.15 arcseconds drift across 512 pixels
        # (Probably OK).
        self.assertAlmostEqual(abs(coord_dist_deg), abs(pix_dist_deg), places=6)



