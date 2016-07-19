import os
import unittest
import tkp.steps.persistence
from tkp.testutil.decorators import requires_mongodb
import tkp.testutil.data as testdata
from tkp.testutil.decorators import requires_database, requires_data
import tkp.db
import tkp.db.generic
import tkp.accessors
from ConfigParser import SafeConfigParser

from tkp.config import parse_to_dict, initialize_pipeline_config
from tkp.testutil.data import default_job_config, default_pipeline_config

datafile = os.path.join(testdata.DATAPATH, "sourcefinder/NCP_sample_image_1.fits")


class TestPersistence(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    @requires_data(datafile)
    @requires_database()
    def setUpClass(cls):
        dataset = tkp.db.DataSet(data={'description': "Test persistence"})
        cls.dataset_id = dataset.id
        cls.images = [datafile]
        cls.accessors = [tkp.accessors.open(datafile)]
        cls.extraction_radius = 256
        job_config = SafeConfigParser()
        job_config.read(default_job_config)
        job_config = parse_to_dict(job_config)
        cls.persistence_pars = job_config['persistence']
        pipe_config = initialize_pipeline_config(default_pipeline_config,
                                                 job_name="test_persistence")

        cls.image_cache_pars = pipe_config['image_cache']


    def test_create_dataset(self):
        dataset_id = tkp.steps.persistence.create_dataset(-1, "test")
        tkp.steps.persistence.create_dataset(dataset_id, "test")

    def test_extract_metadatas(self):
        tkp.steps.persistence.extract_metadatas(self.accessors,
                                                rms_est_sigma=4,
                                                rms_est_fraction=8)

    def test_store_images(self):
        images_metadata = tkp.steps.persistence.extract_metadatas(
            self.accessors, rms_est_sigma=4, rms_est_fraction=8)
        img_ids = tkp.steps.persistence.store_images_in_db(images_metadata,
                                                           self.extraction_radius,
                                                           self.dataset_id,
							   0.0)
        # xtr_radius >=0 is a Postgres constraint, but we should also test
        # manually, in case running MonetDB:
        for id in img_ids:
            image = tkp.db.Image(id=id)
            skyrgn = tkp.db.generic.columns_from_table('skyregion',
                                                   where=dict(id=image.skyrgn))
            self.assertGreaterEqual(skyrgn[0]['xtr_radius'], 0)

    def test_safe_to_mongodb(self):
        tkp.steps.persistence.save_to_mongodb(self.images,
                                              self.image_cache_pars)


@requires_mongodb()
class TestMongoDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images = [datafile]

    @unittest.skip("disabled for now since no proper way to configure (yet)")
    def test_image_to_mongodb(self):
        self.assertTrue(tkp.steps.persistence.image_to_mongodb(self.images[0],
                                                    hostname, port, database))
