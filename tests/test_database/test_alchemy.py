import unittest
import logging
from datetime import datetime, timedelta

import tkp.db
import tkp.db.model
import tkp.db.alchemy


logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


def gen_band(central=150**6, low=None, high=None):
    if not low:
        low = central * .9
    if not high:
        high = central * 1.1
    return tkp.db.model.Frequencyband(freq_low=low, freq_central=central,
                                      freq_high=high)


def gen_dataset(description):
    return tkp.db.model.Dataset(process_start_ts=datetime.now(),
                                description=description)


def gen_skyregion(dataset):
    return tkp.db.model.Skyregion(dataset=dataset, centre_ra=1, centre_decl=1,
                                  xtr_radius=1, x=1, y=1, z=1)


def gen_image(band, dataset, skyregion, taustart_ts=None):
    if not taustart_ts:
        taustart_ts = datetime.now()
    return tkp.db.model.Image(band=band, dataset=dataset, skyrgn=skyregion,
                              freq_eff=2, rb_smin=1, taustart_ts=taustart_ts,
                              rb_smaj=1, rb_pa=1, deltax=1, deltay=1, rms_qc=0)


def gen_extractedsource(image):
    return tkp.db.model.Extractedsource(zone=1, ra=1, decl=1, uncertainty_ew=1, x=1, y=1,
                                        z=1, uncertainty_ns=1, ra_err=1, decl_err=1,
                                        ra_fit_err=1, decl_fit_err=1, ew_sys_err=1,
                                        ns_sys_err=1, error_radius=1, racosdecl=1,
                                        det_sigma=1, f_int=0.01, image=image)


def gen_runningcatalog(xtrsrc, dataset):
    return tkp.db.model.Runningcatalog(xtrsrc=xtrsrc, dataset=dataset, datapoints=1,
                                       zone=1, wm_ra=1., wm_decl=1, wm_uncertainty_ew=1,
                                       wm_uncertainty_ns=1, avg_ra_err=1, avg_decl_err=1,
                                       avg_wra=1, avg_wdecl=1, avg_weight_ra=1, avg_weight_decl=1,
                                       x=1, y=1, z=1)


def gen_assocxtrsource(runningcatalog, xtrsrc):
    return tkp.db.model.Assocxtrsource(runcat=runningcatalog, xtrsrc=xtrsrc,
                                       type=0, r=0, distance_arcsec=0, v_int=0,
                                       eta_int=0, f_datapoints=0)


def gen_newsource(runcat, xtrsrc, image):
    return tkp.db.model.Newsource(runcat=runcat, trigger_xtrsrc=xtrsrc,
                                  newsource_type=1, previous_limits_image=image)


def gen_lightcurve(band, dataset, skyregion, datapoints=10):
    """
    returns: a list of created SQLAlchemy objects
    """
    start = datetime.fromtimestamp(0)
    ten_sec = timedelta(seconds=10)
    xtrsrcs = []
    images = []
    assocs = []
    for i in range(datapoints):
        taustart_ts = start + ten_sec * i
        image = gen_image(band, dataset, skyregion, taustart_ts)

        if i == 5:
            image.int = 10
        images.append(image)
        xtrsrcs.append(gen_extractedsource(image))

    # now we can make runningcatalog, we use first xtrsrc as trigger src
    runningcatalog = gen_runningcatalog(xtrsrcs[0], dataset)

    # create the associations. Can't do this directly since the
    # association table has non nullable columns
    for xtrsrc in xtrsrcs:
        assocs.append(gen_assocxtrsource(runningcatalog, xtrsrc))

    newsource = gen_newsource(runningcatalog, xtrsrcs[5], images[4])

    # just return all db objects we created
    return [dataset, band, skyregion, runningcatalog, newsource] + images + \
           xtrsrcs + assocs


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = tkp.db.Database()
        cls.db.connect()

    def setUp(self):
        self.session = self.db.Session()

        # make 2 datasets with 2 lightcurves each. Lightcurves have different
        # band
        band1 = gen_band(central=150**6)
        band2 = gen_band(central=160**6)
        self.dataset1 = gen_dataset('sqlalchemy test')
        self.dataset2 = gen_dataset('sqlalchemy test')
        skyregion1 = gen_skyregion(self.dataset1)
        skyregion2 = gen_skyregion(self.dataset2)
        lightcurve1 = gen_lightcurve(band1, self.dataset1, skyregion1)
        lightcurve2 = gen_lightcurve(band2, self.dataset1, skyregion1)
        lightcurve3 = gen_lightcurve(band1, self.dataset2, skyregion2)
        lightcurve4 = gen_lightcurve(band2, self.dataset2, skyregion2)
        db_objecsts = lightcurve1 + lightcurve2 + lightcurve3 + lightcurve4
        self.session.add_all(db_objecsts)
        self.session.flush()
        self.session.commit()

    def test_last_assoc_timestamps(self):
        q = tkp.db.alchemy._last_assoc_timestamps(self.session, self.dataset1)
        r = self.session.query(q).all()
        self.assertEqual(len(r), 2)  # we have two bands

    def test_last_assoc_per_band(self):
        q = tkp.db.alchemy._last_assoc_per_band(self.session, self.dataset1)
        r = self.session.query(q).all()
        self.assertEqual(len(r), 2)  # we have two bands

    def test_last_ts_fmax(self):
        q = tkp.db.alchemy._last_ts_fmax(self.session, self.dataset1)
        r = self.session.query(q).all()[0]
        self.assertEqual(r.max_flux, 0.01)

    def test_newsrc_trigger(self):
        q = tkp.db.alchemy._newsrc_trigger(self.session, self.dataset1)
        self.session.query(q).all()

    def test_combined(self):
        q = tkp.db.alchemy._combined(self.session, self.dataset1)
        r = list(self.session.query(q).all()[0])
        r = [item for i, item in enumerate(r) if i not in (0, 5, 6, 10, 11, 16)]
        shouldbe = [1.0, 1.0, 1.0, 1.0, 1, 0.0, 0.0, None, None, 0.01, 0.01]
        self.assertEqual(r, shouldbe)

    def test_transient(self):
        r = tkp.db.alchemy.transients(self.session, self.dataset1).all()
        self.assertEqual(len(r), 2)

    def test_transient_region(self):
        """
        Ra & Decl filtering
        """
        r = tkp.db.alchemy.transients(self.session, self.dataset1, ra_range=(0, 2),
                                  decl_range=(0, 2)).all()
        self.assertEqual(len(r), 2)

        r = tkp.db.alchemy.transients(self.session, self.dataset1, ra_range=(20, 22),
                                  decl_range=(20, 22)).all()
        self.assertEqual(len(r), 0)

    def test_transient_cutoff(self):
        """
        V_int & eta_int filtering
        """
        r = tkp.db.alchemy.transients(self.session, self.dataset1, v_int_min=0,
                                  eta_int_min=0).all()
        self.assertEqual(len(r), 2)

        q = tkp.db.alchemy.transients(self.session, self.dataset1, v_int_min=1000,
                                  eta_int_min=0)
        r = q.all()
        self.assertEqual(len(r), 0)

        r = tkp.db.alchemy.transients(self.session, self.dataset1, v_int_min=0,
                                  eta_int_min=1000).all()
        self.assertEqual(len(r), 0)

    def test_transient_newsource(self):
        """
        Ra & Decl filtering
        """
        r = tkp.db.alchemy.transients(self.session, self.dataset1,
                                  new_src_only=True).all()
        self.assertEqual(len(r), 2)
