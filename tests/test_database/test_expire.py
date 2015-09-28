"""
All tests related to the 'expiration' of extracted sources.

Without expiration sources will *always* be extracted, also when the source
was only above the detection threshold for one time. This introduces a lot of
false positive light curves in the case of a noise image, and eventually the
whole image will be monitored.

"""
import unittest
from datetime import datetime, timedelta
import logging

from tkp.db.database import Database
from tkp.db.model import Runningcatalog, Extractedsource, FORCED_FIT,\
    Temprunningcatalog
from tkp.db.nulldetections import get_nulldetections, associate_nd
from tkp.db.associations import _update_1_to_1_runcat

from tkp.testutil.alchemy import gen_band, gen_dataset, gen_skyregion, \
    gen_extractedsource, gen_runningcatalog, gen_assocskyrgn, \
    gen_assocxtrsource, gen_image


logging.basicConfig(level=logging.DEBUG)
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TestExpire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = Database()
        cls.database.connect()

    def tearDown(self):
        self.session.rollback()

    def setUp(self):
        """
        make a dataset with 10 images with 2 ligthcurves + one empty image
        """
        self.session = self.database.Session()
        self.band = gen_band(central=150**6)
        self.dataset = gen_dataset('expiring runningcatalog test')
        skyregion = gen_skyregion(self.dataset)
        datapoints = 10

        start = datetime.fromtimestamp(0)
        ten_sec = timedelta(seconds=10)
        xtrsrcs1 = []
        xtrsrcs2 = []
        images = []
        assocs = []
        for i in range(datapoints):
            taustart_ts = start + ten_sec * i
            image = gen_image(self.band, self.dataset, skyregion, taustart_ts)

            if i == 5:
                image.int = 10
            images.append(image)
            xtrsrcs1.append(gen_extractedsource(image))
            xtrsrcs2.append(gen_extractedsource(image))

        # now we can make runningcatalog, we use first xtrsrc as trigger src
        self.runningcatalog1 = gen_runningcatalog(xtrsrcs1[0], self.dataset)
        runningcatalog2 = gen_runningcatalog(xtrsrcs2[0], self.dataset)
        assocskyrgn1 = gen_assocskyrgn(self.runningcatalog1, skyregion)
        assocskyrgn2 = gen_assocskyrgn(runningcatalog2, skyregion)

        # create the associations. Can't do this directly since the
        # association table has non nullable columns
        for xtrsrc in xtrsrcs1:
            assocs.append(gen_assocxtrsource(self.runningcatalog1, xtrsrc))
        for xtrsrc in xtrsrcs2:
            assocs.append(gen_assocxtrsource(runningcatalog2, xtrsrc))

        self.empty_image = gen_image(self.band, self.dataset, skyregion, taustart_ts)

        self.session.add_all([self.band, skyregion, self.runningcatalog1, runningcatalog2,
                              assocskyrgn1, assocskyrgn2, self.empty_image] +
                             images + xtrsrcs1 + xtrsrcs2 + assocs)
        self.session.flush()
        self.session.commit()

    def test_nulldetections(self):
        """
        Check if get_nulldetections doesn't return expired runcats
        """

        # get all runningcatalog entries, should be two
        runcats = self.session.query(Runningcatalog). \
            filter(Runningcatalog.dataset == self.dataset).all()
        self.assertEqual(len(runcats), 2)

        # get_nulldetections before setting forcefits_count, should be 2
        r = get_nulldetections(self.empty_image.id)
        self.assertEqual(len(r), 2)

        # set the forcedfits_count for one of the ligthcurves
        runcats[0].forcedfits_count = 20
        self.session.commit()

        # fetch nulldetections, should be 1 now
        r = get_nulldetections(self.empty_image.id)
        self.assertEqual(len(r), 1)

    def test_associate_nd(self):
        """
        Check if associate_nd increments the forcedfits_count column
        """
        e = Extractedsource(zone=1, ra=1, decl=1, uncertainty_ew=1, x=1, y=1,
                            z=1, uncertainty_ns=1, ra_err=1, decl_err=1,
                            ra_fit_err=1, decl_fit_err=1, ew_sys_err=1,
                            ns_sys_err=1, error_radius=1, racosdecl=1,
                            det_sigma=1, f_int=0.01, image=self.empty_image,
                            semimajor=1, semiminor=1, pa=1, f_peak=1,
                            f_peak_err=1, f_int_err=1, chisq=1,
                            reduced_chisq=1, extract_type=FORCED_FIT,
                            ff_runcat=self.runningcatalog1)
        self.session.add(e)
        self.session.commit()
        forcedfits_count_pre = self.runningcatalog1.forcedfits_count
        associate_nd(self.empty_image.id)
        self.session.refresh(self.runningcatalog1)
        forcedfits_count_post = self.runningcatalog1.forcedfits_count
        self.assertEqual(forcedfits_count_pre + 1, forcedfits_count_post)

    def test_reset(self):
        """
        Check if 1-to-1 association resets expiration counter to 0
        """
        e = Extractedsource(zone=1, ra=1, decl=1, uncertainty_ew=1, x=1, y=1,
                            z=1, uncertainty_ns=1, ra_err=1, decl_err=1,
                            ra_fit_err=1, decl_fit_err=1, ew_sys_err=1,
                            ns_sys_err=1, error_radius=1, racosdecl=1,
                            det_sigma=1, f_int=0.01, image=self.empty_image,
                            semimajor=1, semiminor=1, pa=1, f_peak=1,
                            f_peak_err=1, f_int_err=1, chisq=1,
                            reduced_chisq=1)
        t = Temprunningcatalog(runcat=self.runningcatalog1, xtrsrc=e,
                               dataset=self.dataset, band=self.band,
                               distance_arcsec=0, r=0, datapoints=10, zone=1,
                               wm_ra=1, wm_decl=1, wm_uncertainty_ew=1,
                               wm_uncertainty_ns=1, avg_ra_err=1,
                               avg_decl_err=1, avg_wra=1, avg_wdecl=1,
                               avg_weight_ra=1, avg_weight_decl=1, x=1, y=1,
                               z=1)
        self.runningcatalog1.forcedfits_counts = 20
        self.session.add_all((e, t))
        self.session.commit()

        _update_1_to_1_runcat()

        self.session.refresh(self.runningcatalog1)
        self.assertEqual(self.runningcatalog1.forcedfits_count, 0)
