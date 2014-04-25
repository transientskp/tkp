import unittest
from tkp.lofar.noise import ANTENNAE_PER_TILE
from tkp.lofar.noise import TILES_PER_CORE_STATION
from tkp.lofar.noise import TILES_PER_REMOTE_STATION
from tkp.lofar.noise import TILES_PER_INTL_STATION
from tkp.lofar.noise import Aeff_dipole

class TestHBAStationEffectiveArea(unittest.TestCase):
    """
    Values taken from table 2 of
    http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti"
    """
    known_values = (
        (120, 600, 1200, 2400),
        (150, 512, 1024, 2048),
        (180, 356, 711, 1422),
        (200, 288, 576, 1152),
        (210, 261, 522, 1045),
        (240, 200, 400, 800)
    )

    def test_known_values(self):
        for freq_eff, core, remote, intl in self.known_values:
            freq_eff *= 1e6 # MHz to Hz

            # The results quoted on the ASTRON web page are approximate -- we
            # just need to get "near enough".
            thresh = 3
            self.assertLess(
                abs(ANTENNAE_PER_TILE * TILES_PER_CORE_STATION * Aeff_dipole(freq_eff) - core),
                thresh
            )
            self.assertLess(
                abs(ANTENNAE_PER_TILE * TILES_PER_REMOTE_STATION * Aeff_dipole(freq_eff) - remote),
                thresh
            )
            self.assertLess(
                abs(ANTENNAE_PER_TILE * TILES_PER_INTL_STATION * Aeff_dipole(freq_eff) - intl),
                thresh
            )
