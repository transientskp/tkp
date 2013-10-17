import unittest
import pyfits
import math
import tempfile
import tkp.steps.persistence
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_mongodb
import tkp.testutil.data as testdata
from tkp.testutil.decorators import requires_database
import tkp.db
import tkp.utility.parset as parset
from tkp.testutil.data import default_parset_paths

@requires_database()
class TestPersistence(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        cls.images = [testdata.fits_file]
        cls.extraction_radius = 256
        with open(default_parset_paths['persistence.parset']) as f:
            cls.parset = parset.read_config_section(f, 'persistence')


    def test_create_dataset(self):
        dataset_id = tkp.steps.persistence.create_dataset(-1, "test")
        tkp.steps.persistence.create_dataset(dataset_id, "test")

    def test_extract_metadatas(self):
        tkp.steps.persistence.extract_metadatas(self.images)

    def test_store_images(self):
        images_metadata = tkp.steps.persistence.extract_metadatas(self.images)
        tkp.steps.persistence.store_images(images_metadata,
                                           self.extraction_radius,
                                           self.dataset_id)

    def test_node_steps(self):
        tkp.steps.persistence.node_steps(self.images, self.parset)

    def test_master_steps(self):
        images_metadata = tkp.steps.persistence.extract_metadatas(self.images)
        tkp.steps.persistence.master_steps(images_metadata,
                                           self.extraction_radius, self.parset)



@requires_mongodb()
class TestMongoDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images = [testdata.fits_file]

    @unittest.skip("disabled for now since no proper way to configure (yet)")
    def test_image_to_mongodb(self):
        self.assertTrue(tkp.steps.persistence.image_to_mongodb(self.images[0],
                                                    hostname, port, database))

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
            h = pyfits.PrimaryHDU()
            h.header.update("CRVAL2", refdec)
            if unit:
                h.header.update("CUNIT2", unit)
            h.writeto(temp_fits.name)
            tkp.steps.persistence.fix_reference_dec(temp_fits.name)
            self.assertLess(abs(pyfits.getheader(temp_fits.name)['CRVAL2']), abs(refdec))
