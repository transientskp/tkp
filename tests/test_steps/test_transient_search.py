import unittest
import tkp.steps.transient_search
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database
from tkp.db import DataSet
from ConfigParser import SafeConfigParser
from tkp.config import parse_to_dict
from tkp.testutil.data import default_job_config

@requires_database()
class TestTransientSearch(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        dataset = DataSet(data={'description': "Test transient search"})
        cls.dataset_id = dataset.id
        # Just insert empty image entries - so we don't expect to find any
        # transients.
        # That's ok because we're just syntax-checking here.
        for dset in db_subs.generate_timespaced_dbimages_data(n_images=4):
            image = tkp.db.Image(dataset=dataset, data=dset)
        config = SafeConfigParser()
        config.read(default_job_config)
        config = parse_to_dict(config)
        cls.parset =config['transient_search']

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        tkp.steps.transient_search.search_transients(image_ids[0], self.parset)
