import unittest
import tempfile
import trap.ingredients.monitoringlist
from tkp.testutil import db_subs, db_queries

class TestMonitoringlist(unittest.TestCase):
    def __init__(self, *args):
        super(TestMonitoringlist, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images()
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.flush()

    def test_mark_sources(self):
        trap.ingredients.monitoringlist.mark_sources(self.dataset_id, self.parset.name)

    def test_update_monitoringlist(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        for image_id in image_ids:
            trap.ingredients.monitoringlist.update_monitoringlist(image_id)
