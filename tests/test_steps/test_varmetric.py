import unittest
import logging

import tkp.db.model

from tkp.testutil.alchemy import gen_band, gen_dataset, gen_skyregion,\
    gen_lightcurve

import tkp.db
import tkp.db.alchemy

from tkp.steps.varmetric import execute_store_varmetric


logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = tkp.db.Database()
        cls.db.connect()

    def setUp(self):
        self.session = self.db.Session()

        band = gen_band(central=150**6)
        self.dataset = gen_dataset('test varmetric step')
        skyregion = gen_skyregion(self.dataset)
        lightcurve = gen_lightcurve(band, self.dataset, skyregion)
        self.session.add_all(lightcurve)
        self.session.flush()
        self.session.commit()

    def test_execute_store_varmetric(self):
        session = self.db.Session()
        execute_store_varmetric(session=session, dataset_id=self.dataset.id)
