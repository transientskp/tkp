"""
Makes sure the accessors are pickleable
"""

from future import standard_library
standard_library.install_aliases()
from os import path
import unittest
import pickle
from astropy.io.fits import open as open_fits
from tkp.testutil.data import DATAPATH
from tkp.accessors.fitsimage import FitsImage
from tkp.accessors.fitsimageblob import FitsImageBlob
from tkp.accessors.aartfaaccasaimage import AartfaacCasaImage
from tkp.accessors.lofarcasaimage import LofarCasaImage

AARTFAAC_FITS = path.join(DATAPATH, 'accessors/aartfaac.fits')
CASA_TABLE = path.join(DATAPATH, 'casatable/L55596_000TO009_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')
AARTFAAC_TABLE = path.join(DATAPATH, 'accessors/aartfaac.table')


class TestAccessorPickle(unittest.TestCase):
    def test_fits_pickle(self):
        accessor = FitsImage(AARTFAAC_FITS)
        pickled = pickle.dumps(accessor)
        unpickled = pickle.loads(pickled)
        self.assertEqual(type(unpickled), type(accessor))

    def test_fitsblob_pickle(self):
        fits = open_fits(AARTFAAC_FITS)
        accessor = FitsImageBlob(fits)
        pickled = pickle.dumps(accessor)
        unpickled = pickle.loads(pickled)
        self.assertEqual(type(unpickled), type(accessor))

    def test_lofar_casatable_pickle(self):
        accessor = LofarCasaImage(CASA_TABLE)
        pickled = pickle.dumps(accessor)
        unpickled = pickle.loads(pickled)
        self.assertEqual(type(unpickled), type(accessor))

    def test_aartfaac_casatable_pickle(self):
        accessor = AartfaacCasaImage(AARTFAAC_TABLE)
        pickled = pickle.dumps(accessor)
        unpickled = pickle.loads(pickled)
        self.assertEqual(type(unpickled), type(accessor))
