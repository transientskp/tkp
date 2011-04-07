# Tests for simulated LOFAR datasets.

import unittest
import os
import tkp.sourcefinder.accessors as accessors
import tkp.sourcefinder.image as image
import tkp.utility.coordinates as coords
from tkp.settings import datapath

# The different sections (observed, corrected, model) of the MeasurementSet
# contain different simulations.

# NB A glitch in the simulation code causes a factor of 2 error in measured
# flux.
fudgefactor = 0.5

class L15_12h_const_obs(unittest.TestCase):
    # Single, constant 1 Jy source at centre of image.
    def setUp(self):
        # Beam here is a random beam, in this case the WENSS beam without the declination dependence.
        self.myff = accessors.FitsFile(os.path.join(datapath, 'L15_12h_const/observed-all.fits'),beam=(54./3600,54./3600,0.))
        self.myim = image.ImageData(self.myff)
        self.sex  = self.myim.sextract(det=10)

    def testNumSources(self):
        self.assertEqual(len(self.sex), 1)

    def testSourceProperties(self):
        mysource = self.sex.closest_to(1440, 1440)[0]
        self.assertAlmostEqual(mysource.peak, 1.0 * fudgefactor, 1)

    def tearDown(self):
        del(self.sex)
        del(self.myim)
        del(self.myff)


class L15_12h_const_cor(unittest.TestCase):
    # Cross shape of 5 sources, 2 degrees apart, at centre of image.
    def setUp(self):
        # Beam here is a random beam, in this case the WENSS beam without the declination dependence.
        self.myff = accessors.FitsFile(os.path.join(datapath, 'L15_12h_const/corrected-all.fits'),beam=(54./3600,54./3600,0.))
        self.myim = image.ImageData(self.myff)
        self.sex  = self.myim.sextract(det=10)

    def testNumSources(self):
        self.assertEqual(len(self.sex), 5)

    def testFluxes(self):
        # All sources in this image are supposed to have the same flux.
        # But they don't, because the simulation is broken, so this test
        # checks they fall in a vaguely plausible range.
        for mysource in self.sex:
            self.assert_(mysource.peak.value > 0.35)
            self.assert_(mysource.peak.value < 0.60)

    def testSeparation(self):
        centre = self.sex.closest_to(1440, 1440)[0]
        # How accurate should the '2 degrees' be?
        for mysource in filter(lambda src: src != centre, self.sex):
            self.assertAlmostEqual(round(coords.angsep(centre.ra, centre.dec, mysource.ra, mysource.dec) / 60**2), 2)

    def tearDown(self):
        del(self.sex)
        del(self.myim)
        del(self.myff)


class L15_12h_const_mod(unittest.TestCase):
    # 1 Jy constant source at centre; 1 Jy (peak) transient 3 degrees away.
    def setUp(self):
        # This image is of the whole sequence, so obviously we won't see the
        # transient varying. In fact, due to a glitch in the simulation
        # process, it will appear smeared out & shouldn't be identified at
        # all.
        # Beam here is a random beam, in this case the WENSS beam without the declination dependence.
        self.myff = accessors.FitsFile(os.path.join(datapath, 'L15_12h_const/model-all.fits'),beam=(54./3600,54./3600,0.))
        self.myim = image.ImageData(self.myff)
        self.sex  = self.myim.sextract(det=5)

    def testNumSources(self):
        self.assertEqual(len(self.sex), 1)

    def testFluxes(self):
        self.sex.sort(lambda x, y: cmp(y.peak, x.peak))
        self.assertAlmostEqual(self.sex[0].peak.value, 1.0 * fudgefactor, 1)

    def tearDown(self):
        del(self.sex)
        del(self.myim)
        del(self.myff)

class FitToPointTestCase(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(datapath, "L15_12h_const/corrected-all.fits")
        # Beam here is a random beam, in this case the WENSS beam without the declination dependence.
        self.my_im = image.ImageData(accessors.FitsFile(filename,beam=(54./3600,54./3600,0.)))

    def testFixed(self):
        d = self.my_im.fit_to_point(1379.00938273, 1438.38801493, 20, threshold=2)
        self.assertAlmostEqual(d.x.value, 1379.00938273)
        self.assertAlmostEqual(d.y.value, 1438.38801493)

    def testUnFixed(self):
        d = self.my_im.fit_to_point(1379.00938273, 1438.38801493, 20, threshold=2, fixed=None)
        self.assertAlmostEqual(d.x.value, 1379.00938273, 0)
        self.assertAlmostEqual(d.y.value, 1438.38801493, 0)



if __name__ == '__main__':
    unittest.main()
