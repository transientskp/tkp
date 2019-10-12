from os import path
import unittest
import cPickle
from astropy.io import fits
from astropy.io.fits.header import Header
from tkp.db.image_store import store_fits
from tkp.db.model import Image
from tkp.db.database import Database
from tkp.testutil.data import DATAPATH
from tkp.testutil.alchemy import gen_image
from tkp.testutil.decorators import requires_database

FITS_FILE = path.join(DATAPATH, 'accessors/aartfaac.fits')



class TestImageStore(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.db = Database()
        self.image = gen_image()
        self.db.session.add(self.image)
        self.db.session.flush()

    def test_image_store(self):
        fits_object = fits.open(FITS_FILE)
        expected_data = cPickle.dumps(fits_object[0].data)
        expected_header = fits_object[0].header
        store_fits([self.image], [expected_data], [str(expected_header)])
        fetched_image = self.db.session.query(Image).filter(Image.id==self.image.id).first()
        returned_data = cPickle.loads(fetched_image.data.fits_data)
        returned_header = Header.fromstring(fetched_image.data.fits_header)
        self.assertTrue((returned_data, expected_data))
        self.assertEqual(returned_header, expected_header)
