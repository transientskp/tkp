# Tests for simulated LOFAR datasets.

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
from tkp.utility import accessors
import tkp.sourcefinder.image as image
import tkp.utility.coordinates as coords
import tkp.config
from tkp.testutil.decorators import requires_data

DATAPATH = tkp.config.config['test']['datapath']
# The simulation code causes a factor of 2 difference in the
# measured flux.
FUDGEFACTOR = 0.5

# The different sections (observed, corrected, model) of the
# MeasurementSet contain different simulations.

class L15_12hConstObs(unittest.TestCase):
    # Single, constant 1 Jy source at centre of image.
    def setUp(self):
        # Beam here is a random beam, in this case the WENSS beam
        # without the declination dependence.
        fitsfile = accessors.FitsFile(os.path.join(
            DATAPATH, 'L15_12h_const/observed-all.fits'),
                                      beam=(54./3600, 54./3600, 0.))
        self.image = image.ImageData(fitsfile.data, fitsfile.beam, fitsfile.wcs)
        self.results = self.image.extract(det=10)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testNumSources(self):
        self.assertEqual(len(self.results), 1)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def testSourceProperties(self):
        mysource = self.results.closest_to(1440, 1440)[0]
        self.assertAlmostEqual(mysource.peak, 1.0*FUDGEFACTOR, 1)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/observed-all.fits'))
    def tearDown(self):
        del(self.results)
        del(self.image)


class L15_12hConstCor(unittest.TestCase):
    # Cross shape of 5 sources, 2 degrees apart, at centre of image.
    def setUp(self):
        # Beam here is a random beam, in this case the WENSS beam
        # without the declination dependence.
        fitsfile = accessors.FitsFile(os.path.join(
            DATAPATH, 'L15_12h_const/corrected-all.fits'),
                                      beam=(54./3600, 54./3600, 0.))
        self.image = image.ImageData(fitsfile.data, fitsfile.beam, fitsfile.wcs)
        self.results  = self.image.extract(det=10)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/corrected-all.fits'))
    def testNumSources(self):
        self.assertEqual(len(self.results), 5)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/corrected-all.fits'))
    def testFluxes(self):
        # All sources in this image are supposed to have the same flux.
        # But they don't, because the simulation is broken, so this test
        # checks they fall in a vaguely plausible range.
        for mysource in self.results:
            self.assert_(mysource.peak.value > 0.35)
            self.assert_(mysource.peak.value < 0.60)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/corrected-all.fits'))
    def testSeparation(self):
        centre = self.results.closest_to(1440, 1440)[0]
        # How accurate should the '2 degrees' be?
        for mysource in filter(lambda src: src != centre, self.results):
            self.assertAlmostEqual(round(
                coords.angsep(centre.ra, centre.dec, mysource.ra, mysource.dec) /
                60**2), 2)

    def tearDown(self):
        del(self.results)
        del(self.image)


class L15_12hConstMod(unittest.TestCase):
    # 1 Jy constant source at centre; 1 Jy (peak) transient 3 degrees away.
    def setUp(self):
        # This image is of the whole sequence, so obviously we won't see the
        # transient varying. In fact, due to a glitch in the simulation
        # process, it will appear smeared out & shouldn't be identified at
        # all.
        # Beam here is a random beam, in this case the WENSS beam
        # without the declination dependence.
        fitsfile = accessors.FitsFile(os.path.join(
            DATAPATH, 'L15_12h_const/model-all.fits'),
                                      beam=(54./3600, 54./3600, 0.))
        self.image = image.ImageData(fitsfile.data, fitsfile.beam, fitsfile.wcs)
        self.results  = self.image.extract(det=5)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/model-all.fits'))
    def testNumSources(self):
        self.assertEqual(len(self.results), 1)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/model-all.fits'))
    def testFluxes(self):
        self.results.sort(lambda x, y: cmp(y.peak, x.peak))
        self.assertAlmostEqual(self.results[0].peak.value, 1.0*FUDGEFACTOR, 1)

    def tearDown(self):
        del(self.results)
        del(self.image)


class FitToPointTestCase(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(DATAPATH, "L15_12h_const/corrected-all.fits")
        # Beam here is a random beam, in this case the WENSS beam
        # without the declination dependence.
        fitsfile = accessors.FitsFile(filename, beam=(54./3600, 54./3600, 0.))
        self.my_im = image.ImageData(fitsfile.data, fitsfile.beam,
                                     fitsfile.wcs)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/corrected-all.fits'))
    def testFixed(self):
        d = self.my_im.fit_to_point(1379.00938273, 1438.38801493, 20,
                                    threshold=2, fixed='position')
        self.assertAlmostEqual(d.x.value, 1379.00938273)
        self.assertAlmostEqual(d.y.value, 1438.38801493)

    @requires_data(os.path.join(DATAPATH, 'L15_12h_const/corrected-all.fits'))
    def testUnFixed(self):
        d = self.my_im.fit_to_point(1379.00938273, 1438.38801493, 20,
                                    threshold=2, fixed=None)
        self.assertAlmostEqual(d.x.value, 1379.00938273, 0)
        self.assertAlmostEqual(d.y.value, 1438.38801493, 0)


if __name__ == '__main__':
    unittest.main()
