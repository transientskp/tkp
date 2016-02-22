import unittest
import astropy.io.fits as fits
import math
import tempfile
from tkp.utility.fits import fix_reference_dec

class TestFixReferenceDec(unittest.TestCase):
    def test_dec_90(self):
        # Default unit is degrees.
        self._test_for_reference_dec(90.0)

    def test_dec_minus90(self):
        # Default unit is degrees.
        self._test_for_reference_dec(-90.0)

    def test_dec_90_deg(self):
        self._test_for_reference_dec(90.0, "deg")

    def test_dec_pi_by_2_rad(self):
        self._test_for_reference_dec(math.pi/2, "rad")

    def _test_for_reference_dec(self, refdec, unit=None):
        with tempfile.NamedTemporaryFile() as temp_fits:
            h = fits.PrimaryHDU()
            h.header["CRVAL2"] = refdec
            if unit:
                h.header.update("CUNIT2", unit)
            h.writeto(temp_fits.name)
            fix_reference_dec(temp_fits.name)
            self.assertLess(abs(fits.getheader(temp_fits.name)['CRVAL2']), abs(refdec))
