import unittest
import logging
from datetime import datetime, timedelta

import tkp.db
import tkp.db.alchemy.varmetric
import tkp.db.model


from tkp.testutil.alchemy import gen_band, gen_dataset, gen_skyregion, \
    gen_lightcurve
from tkp.testutil.decorators import database_disabled

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Can't use a regular skip here, due to a Nose bug:
        # https://github.com/nose-devs/nose/issues/946
        if database_disabled():
            raise unittest.SkipTest("Database functionality disabled "
                                    "in configuration.")
        cls.db = tkp.db.Database()
        cls.db.connect()

    def setUp(self):
        self.session = self.db.Session()

        # make 2 datasets with 2 lightcurves each. Lightcurves have different
        # band
        self.dataset1 = gen_dataset('sqlalchemy test')
        self.dataset2 = gen_dataset('sqlalchemy test')
        d1_b1 = gen_band(dataset=self.dataset1, central=150**6)
        d1_b2 = gen_band(dataset=self.dataset1, central=160**6)
        d2_b1 = gen_band(dataset=self.dataset2, central=150**6)
        d2_b2 = gen_band(dataset=self.dataset2, central=160**6)

        skyregion1 = gen_skyregion(self.dataset1)
        skyregion2 = gen_skyregion(self.dataset2)
        lightcurve1 = gen_lightcurve(d1_b1, self.dataset1, skyregion1)
        lightcurve2 = gen_lightcurve(d1_b2, self.dataset1, skyregion1)
        lightcurve3 = gen_lightcurve(d2_b1, self.dataset2, skyregion2)
        lightcurve4 = gen_lightcurve(d2_b2, self.dataset2, skyregion2)
        db_objecsts = lightcurve1 + lightcurve2 + lightcurve3 + lightcurve4
        self.session.add_all(db_objecsts)
        self.session.flush()
        self.session.commit()

    def test_last_assoc_timestamps(self):
        q = tkp.db.alchemy.varmetric._last_assoc_timestamps(self.session, self.dataset1)
        r = self.session.query(q).all()
        self.assertEqual(len(r), 2)  # we have two bands

    def test_last_assoc_per_band(self):
        q = tkp.db.alchemy.varmetric._last_assoc_per_band(self.session, self.dataset1)
        r = self.session.query(q).all()
        self.assertEqual(len(r), 2)  # we have two bands

    def test_last_ts_fmax(self):
        q = tkp.db.alchemy.varmetric._last_ts_fmax(self.session, self.dataset1)
        r = self.session.query(q).all()[0]
        self.assertEqual(r.max_flux, 0.01)

    def test_newsrc_trigger(self):
        q = tkp.db.alchemy.varmetric._newsrc_trigger(self.session, self.dataset1)
        self.session.query(q).all()

    def test_combined(self):
        q = tkp.db.alchemy.varmetric._combined(self.session, self.dataset1)
        r = list(self.session.query(q).all()[0])
        r = [item for i, item in enumerate(r) if i not in (0, 5, 6, 10, 11, 16)]
        shouldbe = [1.0, 1.0, 1.0, 1.0, 1, 0.0, 0.0, None, None, 0.01, 0.01]
        for x, y in zip(r, shouldbe):
            self.assertAlmostEqual(x, y)

    def test_calculate_varmetric(self):
        r = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1).all()
        self.assertEqual(len(r), 2)

    def test_calculate_varmetric_region(self):
        """
        Ra & Decl filtering
        """
        r = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1,
                                                         ra_range=(0, 2),
                                                         decl_range=(0, 2)).all()
        self.assertEqual(len(r), 2)

        r = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1,
                                                         ra_range=(20, 22),
                                                         decl_range=(20, 22)).all()
        self.assertEqual(len(r), 0)

    def test_calculate_varmetric_cutoff(self):
        """
        V_int & eta_int filtering
        """
        r = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1,
                                                         v_int_min=0,
                                                         eta_int_min=0).all()
        self.assertEqual(len(r), 2)

        q = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1,
                                                         v_int_min=1000,
                                                         eta_int_min=0)
        r = q.all()
        self.assertEqual(len(r), 0)

        r = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1,
                                                         v_int_min=0,
                                                         eta_int_min=1000).all()
        self.assertEqual(len(r), 0)

    def test_calculate_varmetric_newsource(self):
        """
        Ra & Decl filtering
        """
        r = tkp.db.alchemy.varmetric.calculate_varmetric(self.session, self.dataset1,
                                                         new_src_only=True).all()
        self.assertEqual(len(r), 2)

    def test_store_varmetric(self):
        q = tkp.db.alchemy.varmetric.store_varmetric(self.session, self.dataset1)
        self.session.execute(q)
        r = self.session.query(tkp.db.model.Varmetric).\
            join(tkp.db.model.Varmetric.runcat).\
            filter_by(dataset=self.dataset1).all()
        self.assertEqual(len(r), 2)
