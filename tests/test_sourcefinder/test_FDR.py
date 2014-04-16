"""
Here we test the FDR algorithm using two maps with pure Gaussian noise.

In one map the pixels are not spatially correlated, in the other one they
are.  In fact, the second map has been made by convolving a map similar to
the first with the dirty beam of a certain VLA observation.

Analysis shows that the pixel values of the convolved map do not follow an
exact Gaussian distribution in the sense that the number of extreme pixel
values, based on some reasonable estimate of the number of independent
pixels, i.e., based on some reasonable estimate of the correlation length,
exceeds the expected number from Gaussian statistics.  Nevertheless, also
for the convolved image, image.fd_extract will not find any sources for any
reasonable value of alpha.

A similar conclusion was drawn in paragraph 3.8 of Spreeuw's thesis although
these maps were made in a slightly different manner, i.e., by adding
Gaussian noise to the visibilities and, subsequently, an FFT.  Here the
Gaussian noise in an image was convolved with a dirty beam, although FFTs
were used to speed things up (I used scipy.signal.fftconvolve).  We adjusted
the header of UNCORRELATED_NOISE.FITS, by adding values for BMAJ and BMIN
(and BPA, but that is redundant) to make sure that 0.25 * pi* BMAJ * BMIN =
-CDELT1 * CDELT2, i.e., that the correlated area (with the default equations
from config.py) equals the area of exactly one pixel.

Strictly speaking the FDR algorithm applies to the number of falsely
detected pixels as a fraction of all detected pixels.  in the presence of
uncorrelated noise. The algorithm has been modified somewhat to apply it to
correlated noise, but there is no rigorous statistical proof, see Hopkins et
al. (2002), AJ 123, 1086, paragraph 3.1.  Also, it should be noted that the
validity of the FDR algorithm refers to large ensembles.  This means that in
indivual maps the fraction of falsely detected pixels can exceed the
threshold (alpha).  For these unit tests, we'll be bold and use the number
of detected sources in the presence of correlated noise in a single map
(TEST_DECONV.FITS).
"""

import os

import unittest

from tkp import accessors
from tkp.sourcefinder import image
from tkp.testutil.decorators import requires_data, duration
from tkp.testutil.data import DATAPATH


NUMBER_INSERTED = float(3969)


@requires_data(os.path.join(DATAPATH, 'UNCORRELATED_NOISE.FITS'))
@requires_data(os.path.join(DATAPATH, 'CORRELATED_NOISE.FITS'))
@requires_data(os.path.join(DATAPATH, 'TEST_DECONV.FITS'))
@duration(100)
class test_maps(unittest.TestCase):
    def setUp(self):
        uncorr_map = accessors.open(os.path.join(DATAPATH,
                                                 'UNCORRELATED_NOISE.FITS'))
        corr_map = accessors.open(os.path.join(DATAPATH,
                                               'CORRELATED_NOISE.FITS'))
        map_with_sources = accessors.open(os.path.join(DATAPATH,
                                                       'TEST_DECONV.FITS'))

        self.uncorr_image = image.ImageData(uncorr_map.data, uncorr_map.beam,
                                            uncorr_map.wcs)
        self.corr_image = image.ImageData(corr_map.data, uncorr_map.beam,
                                          uncorr_map.wcs)
        self.image_with_sources = image.ImageData(map_with_sources.data,
                                                  map_with_sources.beam,
                                                  map_with_sources.wcs)

    def test_normal(self):
        self.number_detections_uncorr = len(self.uncorr_image.fd_extract())
        self.number_detections_corr = len(self.corr_image.fd_extract())
        self.assertEqual(self.number_detections_uncorr, 0)
        self.assertEqual(self.number_detections_corr, 0)

    def test_alpha0_1(self):
        self.number_alpha_10pc = len(self.image_with_sources.fd_extract(alpha=0.1))
        self.assertTrue((self.number_alpha_10pc - NUMBER_INSERTED) /
                        NUMBER_INSERTED < 0.1)

    def test_alpha0_01(self):
        self.number_alpha_1pc = len(self.image_with_sources.fd_extract(alpha=0.01))
        self.assertTrue((self.number_alpha_1pc - NUMBER_INSERTED) /
                        NUMBER_INSERTED < 0.01)

    def test_alpha0_001(self):
        self.number_alpha_point1pc = len(self.image_with_sources.fd_extract(alpha=0.001))
        self.assertTrue((self.number_alpha_point1pc - NUMBER_INSERTED) /
                        NUMBER_INSERTED < 0.001)


if __name__ == '__main__':
    unittest.main()
