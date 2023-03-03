import os
import unittest

import numpy as np
from tkp import accessors
from tkp.accessors.fitsimage import FitsImage
from tkp.testutil.data import DATAPATH
from tkp.testutil.data import fits_file
from tkp.testutil.decorators import requires_data
from tkp.testutil.mock import SyntheticImage

import tkp.sourcefinder
from tkp.sourcefinder import image as sfimage
from tkp.sourcefinder.image import ImageData
from tkp.utility.uncertain import Uncertain

BOX_IN_BEAMPIX = 10  # HARDCODING - FIXME! (see also monitoringlist recipe)

GRB120422A = os.path.join(DATAPATH, "sourcefinder/GRB120422A-120429.fits")


class TestNumpySubroutines(unittest.TestCase):
    def testBoxSlicing(self):
        """
        Tests a routine to return a window on an image.

        Previous implementation returned correct sized box,
        but central pixel was often offset unnecessarily.
        This method always returns a centred chunk.
        """

        a = np.arange(1, 101)
        a = a.reshape(10, 10)
        x, y = 3, 3
        central_value = a[y, x]  # 34

        round_down_to_single_pixel = a[
            sfimage.ImageData.box_slice_about_pixel(x, y, 0.9)]
        self.assertEqual(round_down_to_single_pixel, [[central_value]])

        chunk_3_by_3 = a[sfimage.ImageData.box_slice_about_pixel(x, y, 1)]
        self.assertEqual(chunk_3_by_3.shape, (3, 3))
        self.assertEqual(central_value, chunk_3_by_3[1, 1])

        chunk_3_by_3_round_down = a[
            sfimage.ImageData.box_slice_about_pixel(x, y, 1.9)]
        self.assertListEqual(list(chunk_3_by_3.reshape(9)),
                             list(chunk_3_by_3_round_down.reshape(9))
                             )


class TestMapsType(unittest.TestCase):
    """
    Check that rms, bg maps are of correct type.
    """

    @requires_data(GRB120422A)
    def testmaps_array_type(self):
        self.image = accessors.sourcefinder_image_from_accessor(
            FitsImage(GRB120422A), margin=10)
        self.assertIsInstance(self.image.rmsmap, np.ma.MaskedArray)
        self.assertIsInstance(self.image.backmap, np.ma.MaskedArray)


class TestFitFixedPositions(unittest.TestCase):
    """Test various fitting cases where the pixel position is predetermined"""

    @requires_data(
        os.path.join(DATAPATH, 'sourcefinder/NCP_sample_image_1.fits'))
    def setUp(self):
        """
        NB the required image has been committed to the tkp/data subversion repository.

        (See tkp/data/unittests/tkp_lib for a full copy of all the unittest data).

        Source positions / background positions were simply picked out by eye in DS9
        """
        self.image = accessors.sourcefinder_image_from_accessor(
            accessors.open(
                os.path.join(DATAPATH, 'sourcefinder/NCP_sample_image_1.fits'))
        )
        self.assertListEqual(list(self.image.data.shape), [1024, 1024])
        self.boxsize = BOX_IN_BEAMPIX * max(self.image.beam[0],
                                            self.image.beam[1])
        self.bright_src_posn = (35.76726, 86.305771)  # RA, DEC
        self.background_posn = (6.33731, 82.70002)  # RA, DEC

        # #NB Peak of forced gaussian fit is simply plucked from a previous run;
        # so merely ensures *consistent*, rather than *correct*, results.
        self.known_fit_results = (self.bright_src_posn[0],  # RA,
                                  self.bright_src_posn[1],  # Dec
                                  13.457697411730384)  # Peak

    def testSourceAtGivenPosition(self):
        posn = self.bright_src_posn
        img = self.image
        results = self.image.fit_fixed_positions(positions=[posn],
                                                 boxsize=self.boxsize,
                                                 threshold=0.0)[0]
        self.assertAlmostEqual(results.ra.value, self.known_fit_results[0],
                               delta=0.01)
        self.assertAlmostEqual(results.dec.value, self.known_fit_results[1],
                               delta=0.01)
        self.assertAlmostEqual(results.peak.value, self.known_fit_results[2],
                               delta=0.01)

    def testLowFitThreshold(self):
        """
        Low fit threshold is equivalent to zero threshold

        If we supply an extremely low threshold
        do we get a similar result to a zero threshold, for a bright source?
        """
        posn = self.bright_src_posn
        img = self.image
        low_thresh_results = self.image.fit_fixed_positions(positions=[posn],
                                                            boxsize=BOX_IN_BEAMPIX * max(
                                                                img.beam[0],
                                                                img.beam[1]),
                                                            threshold=-1e20)[0]
        self.assertAlmostEqual(low_thresh_results.ra.value,
                               self.known_fit_results[0],
                               delta=0.01)
        self.assertAlmostEqual(low_thresh_results.dec.value,
                               self.known_fit_results[1],
                               delta=0.01)
        self.assertAlmostEqual(low_thresh_results.peak.value,
                               self.known_fit_results[2],
                               delta=0.01)

    def testHighFitThreshold(self):
        """
        High fit threshold throws error

        If we supply an extremely high threshold, we expect to get back
        a fitting error since all pixels should be masked out.
        """
        posn = self.bright_src_posn
        img = self.image
        with self.assertRaises(ValueError):
            results = self.image.fit_fixed_positions(positions=[posn],
                                                     boxsize=BOX_IN_BEAMPIX * max(
                                                         img.beam[0],
                                                         img.beam[1]),
                                                     threshold=1e20)

    def testBackgroundAtGivenPosition(self):
        """
        No source at given position (but still in the image frame)

        Note, if we request zero threshold, then the region will be unfittable,
        since it is largely below that thresh.

        Rather than pick an arbitrarily low threshold, we set it to None.
        """

        img = self.image
        results = self.image.fit_fixed_positions(
            positions=[self.background_posn],
            boxsize=BOX_IN_BEAMPIX * max(img.beam[0], img.beam[1]),
            threshold=None
        )[0]
        self.assertAlmostEqual(results.peak.value, 0,
                               delta=results.peak.error * 1.0)

    def testGivenPositionOutsideImage(self):
        """If given position is outside image then result should be NoneType"""
        img = self.image
        # Generate a position halfway up the y-axis, but at negative x-position.
        pixel_posn_negative_x = (-50, img.data.shape[1] / 2.0)
        # and halfway up the y-axis, but at x-position outside array limit:
        pixel_posn_high_x = (img.data.shape[0] + 50, img.data.shape[1] / 2.0)
        sky_posns_out_of_img = [
            img.wcs.p2s(pixel_posn_negative_x),
            img.wcs.p2s(pixel_posn_high_x),
        ]
        # print "Out of image?", sky_posn_out_of_img
        # print "Out of image (pixel backconvert)?", img.wcs.s2p(sky_posn_out_of_img)
        results = self.image.fit_fixed_positions(positions=sky_posns_out_of_img,
                                                 boxsize=BOX_IN_BEAMPIX * max(
                                                     img.beam[0], img.beam[1]))
        self.assertListEqual([], results)

    def testTooCloseToEdgePosition(self):
        """Same if right on the edge -- too few pixels to fit"""
        img = self.image
        boxsize = BOX_IN_BEAMPIX * max(img.beam[0], img.beam[1])
        edge_posn = img.wcs.p2s((0 + boxsize / 2 - 2, img.data.shape[1] / 2.0))
        results = self.image.fit_fixed_positions(
            positions=[edge_posn],
            boxsize=boxsize,
            threshold=-1e10
        )
        self.assertListEqual([], results)

    def testErrorBoxOverlapsEdge(self):
        """
        Error box overflows image

        Sometimes when fitting at a fixed position, we get extremely large
        uncertainty values.  These create an error box on position which
        extends outside the image, causing errors when we try to calculate the
        RA / Dec uncertainties.  This test ensures we handle this case
        gracefully.
        """
        img = self.image

        fake_params = tkp.sourcefinder.extract.ParamSet()
        fake_params.values.update({
            'peak': Uncertain(0.0, 0.5),
            'flux': Uncertain(0.0, 0.5),
            'xbar': Uncertain(5.5, 10000.5),  # Danger Will Robinson
            'ybar': Uncertain(5.5, 3),
            'semimajor': Uncertain(4, 200),
            'semiminor': Uncertain(4, 2),
            'theta': Uncertain(30, 10),
        })
        fake_params.sig = 0
        det = tkp.sourcefinder.extract.Detection(fake_params, img)
        # Raises runtime error prior to bugfix for issue #3294
        det._physical_coordinates()
        self.assertEqual(det.ra.error, float('inf'))
        self.assertEqual(det.dec.error, float('inf'))

    def testForcedFitAtNans(self):
        """
        Should not return a fit if the position was largely masked due to NaNs
        """

        forcedfit_sky_posn = self.bright_src_posn
        forcedfit_pixel_posn = self.image.wcs.s2p(forcedfit_sky_posn)

        fitting_boxsize = BOX_IN_BEAMPIX * max(self.image.beam[0],
                                               self.image.beam[1])

        nandata = self.image.rawdata.copy()
        x0, y0 = forcedfit_pixel_posn

        # If we totally cover the fitting box in NaNs, then there are no
        # valid pixels and fit gets rejected.
        # However, if we only cover the central quarter (containing all the
        # real signal!) then we get a dodgy fit back.
        nanbox_radius = fitting_boxsize / 2
        boxsize_proportion = 0.5
        nanbox_radius *= boxsize_proportion

        nandata[int(x0 - nanbox_radius):int(x0 + nanbox_radius + 1),
        int(y0 - nanbox_radius):int(y0 + nanbox_radius + 1)] = float('nan')

        # Dump image data for manual inspection:
        # import astropy.io.fits as fits
        # # output_data = self.image.rawdata
        # output_data = nandata
        # hdu = fits.PrimaryHDU((output_data).transpose())
        # hdu.writeto('/tmp/nandata.fits',clobber=True)


        nan_image = ImageData(nandata, beam=self.image.beam,
                              wcs=self.image.wcs)

        results = nan_image.fit_fixed_positions(
            positions=[self.bright_src_posn],
            boxsize=fitting_boxsize,
            threshold=None
        )
        print(results)
        self.assertFalse(results)


class TestSimpleImageSourceFind(unittest.TestCase):
    """Now lets test drive the routines which find new sources"""

    @requires_data(GRB120422A)
    def testSingleSourceExtraction(self):
        """
        Single source extaction

        From visual inspection we only expect a single source in the image,
        at around 5 or 6 sigma detection level."""

        ew_sys_err, ns_sys_err = 0.0, 0.0
        known_result = (
            136.89603241069054, 14.022184792492785,  # RA, DEC
            5.341819139061954e-4, 1.3428186757078464e-3,  # Err, Err
            7.226590529214518e-4, 1.0918184742211533e-4,  # Peak flux, err
            6.067963179204716e-4, 1.7037685531724465e-4,
            # Integrated flux, err
            6.192259965962862, 25.516190123153514,
            # Significance level, Beam semimajor-axis width (arcsec)
            10.718798843620489, 178.62899212789304,
            # Beam semiminor-axis width (arcsec), Beam parallactic angle
            ew_sys_err, ns_sys_err,
            5.181697175052841,  # error_radius
            1,  # fit_type
            0.59184643302,  # chisq
            0.67199741142,  # reduced chisq
        )
        self.image = accessors.sourcefinder_image_from_accessor(
            FitsImage(GRB120422A))

        results = self.image.extract(det=5, anl=3)
        results = [result.serialize(ew_sys_err, ns_sys_err) for result in
                   results]
        # Our modified kappa,sigma clipper gives a slightly lower noise
        # which catches an extra noise peak at the 5 sigma level.
        self.assertEqual(len(results), 2)
        r = results[1]
        self.assertEqual(len(r), len(known_result))
        for i in range(len(r)):
            self.assertAlmostEqual(r[i], known_result[i], places=0)

    @requires_data(GRB120422A)
    def testForceSourceShape(self):
        """
        Force source shape to beam

        This image contains a single source (with parameters as listed under
        testSingleSourceExtraction(), above). Here we force the lengths of the
        major/minor axes to be held constant when fitting.
        """
        self.image = accessors.sourcefinder_image_from_accessor(
            FitsImage(GRB120422A))
        results = self.image.extract(det=5, anl=3, force_beam=True)
        self.assertEqual(results[0].smaj.value, self.image.beam[0])
        self.assertEqual(results[0].smin.value, self.image.beam[1])

    @requires_data(os.path.join(DATAPATH, 'sourcefinder/GRB130828A/SWIFT_554620-130504.fits'))
    @requires_data(os.path.join(DATAPATH, 'sourcefinder/GRB130828A/SWIFT_554620-130504.image'))
    def testWcsConversionConsistency(self):
        """
        Check that extracting a source from FITS and CASA versions of the
        same dataset gives the same results (especially, RA and Dec).
        """

        fits_image = accessors.sourcefinder_image_from_accessor(
            FitsImage(os.path.join(DATAPATH, 'sourcefinder/GRB130828A/SWIFT_554620-130504.fits')))
        # Abuse the KAT7 CasaImage class here, since we just want to access
        # the pixel data and the WCS:
        casa_image = accessors.sourcefinder_image_from_accessor(
            accessors.kat7casaimage.Kat7CasaImage(
                os.path.join(DATAPATH, 'sourcefinder/GRB130828A/SWIFT_554620-130504.image')))

        ew_sys_err, ns_sys_err = 0.0, 0.0
        fits_results = fits_image.extract(det=5, anl=3)
        fits_results = [result.serialize(ew_sys_err, ns_sys_err) for result in
                        fits_results]
        casa_results = casa_image.extract(det=5, anl=3)
        casa_results = [result.serialize(ew_sys_err, ns_sys_err) for result in
                        casa_results]
        # Our modified kappa,sigma clipper gives a slightly lower noise
        # which catches two extra noise peaks at the 5 sigma level.
        self.assertEqual(len(fits_results), 3)
        self.assertEqual(len(casa_results), 3)
        fits_src = fits_results[0]
        casa_src = casa_results[0]

        self.assertEqual(len(fits_src), len(casa_src))
        for idx, _ in enumerate(fits_src):
            self.assertAlmostEqual(fits_src[idx], casa_src[idx], places=5)

    @requires_data(GRB120422A)
    def testNoLabelledIslandsCase(self):
        """
        If an image is in fact very boring and flat/empty, then we may not even
        locate any labelled islands, if the analysis threshold is set high enough.

        (We reproduce this test case, even though GRB120422A-120429 has a
        source in the image, just by setting the thresholds very high -
        this avoids requiring additional data).
        """
        self.image = accessors.sourcefinder_image_from_accessor(
            FitsImage(GRB120422A))
        results = self.image.extract(det=5e10, anl=5e10)
        results = [result.serialize() for result in results]
        self.assertEqual(len(results), 0)


class TestMaskedSource(unittest.TestCase):
    """
    Source is masked

    Check that we don't find sources when they fall within a masked region
    of the image.
    """

    @requires_data(GRB120422A)
    def testWholeSourceMasked(self):
        """
        Source in masked region
        """

        self.image = accessors.sourcefinder_image_from_accessor(
            FitsImage(GRB120422A))
        self.image.data[250:280, 250:280] = np.ma.masked
        results = self.image.extract(det=5, anl=3)
        self.assertFalse(results)

    @requires_data(GRB120422A)
    def testWholeSourceMasked(self):
        """
        Part of source masked

        Tip of major axis is around 267, 264
        """

        self.image = accessors.sourcefinder_image_from_accessor(
            FitsImage(GRB120422A))
        self.image.data[266:269, 263:266] = np.ma.masked
        # Our modified kappa,sigma clipper gives a slightly lower noise
        # which catches an extra noise peak at the 5 sigma level.
        self.image.data[42:50, 375:386] = np.ma.masked
        results = self.image.extract(det=5, anl=3)
        self.assertFalse(results)


class TestMaskedBackground(unittest.TestCase):
    # We force the mask by setting the usable region << grid size.
    @requires_data(fits_file)
    def testMaskedBackgroundForcedFit(self):
        """
        Background at forced fit is masked
        """
        self.image = accessors.sourcefinder_image_from_accessor(
            accessors.open(fits_file), radius=1.0)
        result = self.image.fit_to_point(256, 256, 10, 0, None)
        self.assertFalse(result)

    @requires_data(fits_file)
    def testMaskedBackgroundBlind(self):
        self.image = accessors.sourcefinder_image_from_accessor(
            accessors.open(fits_file), radius=1.0)
        result = self.image.extract(det=10.0, anl=3.0)
        self.assertFalse(result)


class TestFailureModes(unittest.TestCase):
    """
    If we get pathological data we should probably throw an exception
    and let the calling code decide what to do.
    """

    def testFlatImage(self):
        sfimage = accessors.sourcefinder_image_from_accessor(
            SyntheticImage(data=np.zeros((512, 512))))
        self.assertTrue(np.ma.max(sfimage.data) == np.ma.min(sfimage.data),
                        msg="Data should be flat")
        with self.assertRaises(RuntimeError):
            sfimage.extract(det=5, anl=3)
