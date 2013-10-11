import unittest
import tkp.steps.persistence
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_mongodb
import tkp.testutil.data as testdata
from tkp.testutil.decorators import requires_database
import tkp.db
from tkp.conf import read_config_section
from tkp.testutil.data import default_job_config

@requires_database()
class TestPersistence(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        cls.images = [testdata.fits_file]
        cls.extraction_radius = 256
        with open(default_job_config) as f:
            cls.parset = read_config_section(f, 'persistence')


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
