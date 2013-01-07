import unittest
import tempfile
import trap.ingredients.persistence
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_mongodb
import tkp.testutil.data as testdata
from tkp.config import config as tkpconfig

class TestPersistence(unittest.TestCase):
    def __init__(self, *args):
        super(TestPersistence, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images()
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.flush()
        self.images = [testdata.fits_file]

    def test_parse_parset(self):
        trap.ingredients.persistence.parse_parset(self.parset.name)

    def test_create_dataset(self):
        dataset_id = trap.ingredients.persistence.create_dataset(-1, "test")
        trap.ingredients.persistence.create_dataset(dataset_id, "test")

    def test_extract_metadatas(self):
        trap.ingredients.persistence.extract_metadatas(self.images)

    def test_store_images(self):
        images_metadata = trap.ingredients.persistence.extract_metadatas(self.images)
        trap.ingredients.persistence.store_images(images_metadata, self.dataset_id)

    def test_node_steps(self):
        trap.ingredients.persistence.node_steps(self.images, self.parset.name)

    def test_master_steps(self):
        images_metadata = trap.ingredients.persistence.extract_metadatas(self.images)
        trap.ingredients.persistence.master_steps(images_metadata, self.parset.name)

    def test_all(self):
        trap.ingredients.persistence.all(self.images, self.parset.name)

@requires_mongodb()
class TestMongoDb(unittest.TestCase):
    def __init__(self, *args):
        super(TestMongoDb, self).__init__(*args)
        self.images = [testdata.fits_file]

    def test_image_to_mongodb(self):
        hostname = tkpconfig['mongodb']['hostname']
        port = tkpconfig['mongodb']['port']
        database = tkpconfig['mongodb']['database']
        self.assertTrue(trap.ingredients.persistence.image_to_mongodb(self.images[0],
                                                    hostname,  port, database))