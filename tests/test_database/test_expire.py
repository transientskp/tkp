"""
All tests related to the 'expiration' of extracted sources.

Without expiration sources will *always* be extracted, also when the source
was only above the detection threshold for one time. This introduces a lot of
false positive light curves in the case of a noise image, and eventually the
whole image will be monitored.

"""
import unittest
from datetime import datetime, timedelta

from tkp.db.database import Database
from tkp.db.model import Runningcatalog
from tkp.db.nulldetections import get_nulldetections, associate_nd

from tkp.testutil.alchemy import gen_band, gen_dataset, gen_skyregion,\
    gen_extractedsource, gen_runningcatalog, gen_assocskyrgn, \
    gen_assocxtrsource, gen_image


class TestExpire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = Database()
        cls.database.connect()

    def setUp(self):
        """
        make a dataset with 10 images with 2 ligthcurves + one empty image
        """
        self.session = self.database.Session()
        band = gen_band(central=150**6)
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
            image = gen_image(band, self.dataset, skyregion, taustart_ts)

            if i == 5:
                image.int = 10
            images.append(image)
            xtrsrcs1.append(gen_extractedsource(image))
            xtrsrcs2.append(gen_extractedsource(image))

        # now we can make runningcatalog, we use first xtrsrc as trigger src
        runningcatalog1 = gen_runningcatalog(xtrsrcs1[0], self.dataset)
        runningcatalog2 = gen_runningcatalog(xtrsrcs2[0], self.dataset)
        assocskyrgn1 = gen_assocskyrgn(runningcatalog1, skyregion)
        assocskyrgn2 = gen_assocskyrgn(runningcatalog2, skyregion)

        # create the associations. Can't do this directly since the
        # association table has non nullable columns
        for xtrsrc in xtrsrcs1:
            assocs.append(gen_assocxtrsource(runningcatalog1, xtrsrc))
        for xtrsrc in xtrsrcs2:
            assocs.append(gen_assocxtrsource(runningcatalog2, xtrsrc))

        self.empty_image = gen_image(band, self.dataset, skyregion, taustart_ts)

        self.session.add_all([band, skyregion, runningcatalog1, runningcatalog2,
                              assocskyrgn1, assocskyrgn2, self.empty_image] +
                             images + xtrsrcs1 + xtrsrcs2 + assocs)
        self.session.flush()
        self.session.commit()

    def test_nulldetections(self):
        """
        Check if get_nulldetections doesn't return expired runcats
        """

        # get all runningcatalog entries, should be two
        runcats = self.session.query(Runningcatalog).\
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
        associate_nd(self.empty_image.id)

    def test_reset(self):
        """
        Check if 1-to-1 association resets expiration counter to 0
        """
        pass

    def test_overall(self):
        """
        Black box test if running catalog entries expire
        """