"""
Try the in memory fits stream Accessor
"""

import os
import unittest
from astropy.io.fits import open as fitsopen
from tkp.accessors import open as tkpopen
from tkp.testutil.data import DATAPATH
from tkp.testutil.decorators import requires_data
from tkp.accessors.fitsimageblob import FitsImageBlob

FITS_FILE = os.path.join(DATAPATH, 'accessors/aartfaac.fits')


@requires_data(FITS_FILE)
class PyfitsFitsImage(unittest.TestCase):

    def setUp(self):
        self.hudelist = fitsopen(FITS_FILE)

    def test_tkp_open(self):
        accessor = tkpopen(FITS_FILE)

    def test_fits_blob_accessor(self):
        accessor = FitsImageBlob(self.hudelist)
