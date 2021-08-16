import unittest
import tkp
from tkp.db import execute, Database
from tkp.testutil import db_subs
from tkp.testutil.decorators import database_disabled
from numpy import median

class testMedian(unittest.TestCase):
    def setUp(self):
        # Can't use a regular skip here, due to a Nose bug:
        # https://github.com/nose-devs/nose/issues/946
        if database_disabled():
            raise unittest.SkipTest("Database functionality disabled "
                                    "in configuration.")
        self.database = tkp.db.Database()

        self.dataset = tkp.db.DataSet(database=self.database,
                                data={'description':"Median test"
                                        + self._testMethodName})
        self.n_images = 5

        self.im_params = db_subs.generate_timespaced_dbimages_data(self.n_images)
        for idx, impar in enumerate(self.im_params):
            impar['rms_max'] = (idx+1)*1e-4

        self.image_ids = []
        for img_pars in self.im_params:
            image,_,_ = db_subs.insert_image_and_simulated_sources(
                    self.dataset,img_pars,[],
                    new_source_sigma_margin=3)
            self.image_ids.append(image.id)


    def test_median(self):
        qry = ("""
          SELECT median(id) as median_id
                ,median(rms_max) as median_rms_max
          FROM image
          WHERE dataset = %(dataset_id)s
          """)
        cursor = execute(qry, {'dataset_id': self.dataset.id})
        results = db_subs.get_db_rows_as_dicts(cursor)
        # self.assertAlmostEqual(results[0]['median_id'], median(self.image_ids))
        self.assertAlmostEqual(results[0]['median_rms_max'],
                         median([p['rms_max'] for p in self.im_params]))

