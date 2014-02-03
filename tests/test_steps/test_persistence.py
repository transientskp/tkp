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
import tkp.db.generic
from ConfigParser import SafeConfigParser
from tkp.conf import parse_to_dict
from tkp.config import initialize_pipeline_config
from tkp.testutil.data import default_job_config, default_pipeline_config
import StringIO

@requires_database()
class TestPersistence(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        cls.images = [testdata.fits_file]
        cls.extraction_radius = 256
        job_config = SafeConfigParser()
        job_config.read(default_job_config)
        job_config = parse_to_dict(job_config)
        cls.job_id_pars = job_config['job_id']
        pipe_config = initialize_pipeline_config(default_pipeline_config,
                                                 job_name="test_persistence")

        cls.image_cache_pars = pipe_config['image_cache']



    def test_create_dataset(self):
        dataset_id = tkp.steps.persistence.create_dataset(-1, "test")
        tkp.steps.persistence.create_dataset(dataset_id, "test")

    def test_extract_metadatas(self):
        tkp.steps.persistence.extract_metadatas(self.images)

    def test_store_images(self):
        images_metadata = tkp.steps.persistence.extract_metadatas(self.images)
        img_ids = tkp.steps.persistence.store_images(images_metadata,
                                           self.extraction_radius,
                                           self.dataset_id)
        # xtr_radius >=0 is a Postgres constraint, but we should also test
        # manually, in case running MonetDB:
        for id in img_ids:
            image = tkp.db.Image(id=id)
            skyrgn = tkp.db.generic.columns_from_table('skyregion',
                                                   where=dict(id=image.skyrgn))
            self.assertGreaterEqual(skyrgn[0]['xtr_radius'], 0)

    def test_node_steps(self):
        tkp.steps.persistence.node_steps(self.images, self.image_cache_pars)

    def test_master_steps(self):
        images_metadata = tkp.steps.persistence.extract_metadatas(self.images)
        tkp.steps.persistence.master_steps(images_metadata,
                                           self.extraction_radius, self.job_id_pars)



@requires_mongodb()
class TestMongoDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images = [testdata.fits_file]

    @unittest.skip("disabled for now since no proper way to configure (yet)")
    def test_image_to_mongodb(self):
        self.assertTrue(tkp.steps.persistence.image_to_mongodb(self.images[0],
                                                    hostname, port, database))
