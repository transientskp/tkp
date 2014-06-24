import datetime
import itertools

import unittest

import tkp.db
from tkp.db import associations as dbass
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db.orm import DataSet
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database

# Use a default argument value for convenience
from functools import partial
associate_extracted_sources = partial(dbass.associate_extracted_sources,
                                      new_source_sigma_margin=3)

@requires_database()
class TestForcedFit(unittest.TestCase):
    """
    These tests will check that monitoringlist sources are associated only amongst themselves.
    """
    def shortDescription(self):
        """http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/"""
        return None

    def tearDown(self):
        tkp.db.rollback()

    def test_monitoringSource(self):
        data = {'description': "monitoringlist:" + self._testMethodName}
        dataset = DataSet(data=data)

        # Three timesteps, 1 band -> 3 images.
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1),
                        datetime.datetime(2013, 10, 1)]
        #freq_effs = [124, 149, 156, 185]
        freq_effs = [124]
        freq_effs = [f * 1e6 for f in freq_effs]

        im_params = db_subs.generate_timespaced_dbimages_data(len(freq_effs)
                                                     * len(taustart_tss))
        timestamps = itertools.repeat(taustart_tss, len(freq_effs))

        for im, freq, ts in zip(im_params, itertools.cycle(freq_effs),
                                itertools.chain.from_iterable(zip(*timestamps))):
            im['freq_eff'] = freq
            im['taustart_ts'] = ts

        images = []
        for im in im_params:
            image = tkp.db.Image(dataset=dataset, data=im)
            images.append(image)

        # Arbitrary parameters, except that they fall inside our image.
        # We have one to be monitored source and one "normal" source
        src0 = db_subs.example_extractedsource_tuple(ra=122.5, dec=9.5)
        src1_mon = db_subs.example_extractedsource_tuple(ra=123.5, dec=10.5)

        # Group images in blocks of 1, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # The "normal" source is seen at all timesteps
                dbgen.insert_extracted_sources(image.id, [src0], 'blind')

            for image in images:
                associate_extracted_sources(image.id, deRuiter_r=5.68)
                # The monitoring sources are the positional inputs for the forced
                # fits, which on their turn return additional parameters,
                # e.g. from src0_mon
                # src1_mon is the monitoring source at all timesteps
                dbgen.insert_extracted_sources(image.id, [src1_mon], 'ff_ms')

                # And here we have to associate the monitoring sources with the
                # runcat sources...
                dbmon.associate_ms(image.id)

        query = """\
        SELECT id
              ,mon_src
          FROM runningcatalog r
         WHERE dataset = %(dataset_id)s
           AND datapoints = 3
        ORDER BY id
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog sources, one for the "normal"
        # source and one for the monitoring source.
        # Both should have three datapoints.
        print "dp_result:",result
        self.assertEqual(len(result), 2)
        # The first source is the "normal" one
        self.assertEqual(result[0][1], False)
        # The second source is the monitoring one
        self.assertEqual(result[1][1], True)

        query = """\
        SELECT r.id
              ,r.mon_src
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset_id)s
           AND rf.runcat = r.id
        ORDER BY r.id
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog_flux entries,
        # one for every source, where every source has
        # three f_datapoints
        self.assertEqual(len(result), 2)

        # "Normal" source: three flux datapoints
        self.assertEqual(result[0][1], False)
        self.assertEqual(result[0][2], 3)
        # Monitoring source: three flux datapoints
        self.assertEqual(result[1][1], True)
        self.assertEqual(result[1][2], 3)

        # We should also have two lightcurves for both sources,
        # where both sources have three datapoints.
        # The association types of the "normal" source are
        # 3 (first) or 4 (later ones), while the monitoring source
        # association types are 8 (first) or 9 (later ones).
        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.type
              ,i.taustart_ts
              ,r.mon_src
              ,x.extract_type
          FROM assocxtrsource a
              ,extractedsource x
              ,image i
              ,runningcatalog r
         WHERE a.xtrsrc = x.id
           AND x.image = i.id
           AND i.dataset = %(dataset_id)s
           AND a.runcat = r.id
        ORDER BY a.runcat
                ,i.taustart_ts
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # 3 + 3 entries for source 1 and 2 resp.
        self.assertEqual(len(result), 6)

        # The individual light-curve datapoints for the "normal" source
        # It was new at first timestep
        self.assertEqual(result[0][2], 4)
        self.assertEqual(result[0][3], taustart_tss[0])
        self.assertEqual(result[0][4], False)
        self.assertEqual(result[0][5], 0)

        # It was known at second timestep
        self.assertEqual(result[1][2], 3)
        self.assertEqual(result[1][3], taustart_tss[1])
        self.assertEqual(result[1][4], result[0][4])
        self.assertEqual(result[1][5], result[0][5])

        # It was known at third timestep
        self.assertEqual(result[2][2], result[1][2])
        self.assertEqual(result[2][3], taustart_tss[2])
        self.assertEqual(result[2][4], result[1][4])
        self.assertEqual(result[2][5], result[1][5])

        # The individual light-curve datapoints for the monitoring source
        # It was new at first timestep
        self.assertEqual(result[3][2], 8)
        self.assertEqual(result[3][3], taustart_tss[0])
        self.assertEqual(result[3][4], True)
        self.assertEqual(result[3][5], 2)

        # It was known at second timestep
        self.assertEqual(result[4][2], 9)
        self.assertEqual(result[4][3], taustart_tss[1])
        self.assertEqual(result[4][4], result[3][4])
        self.assertEqual(result[4][5], result[3][5])

        # It was known at third timestep
        self.assertEqual(result[5][2], result[4][2])
        self.assertEqual(result[5][3], taustart_tss[2])
        self.assertEqual(result[5][4], result[4][4])
        self.assertEqual(result[5][5], result[4][5])

    def test_monitoringSourceSamePos(self):
        """Here we test the case when the monitoring source position
        is identical to a blindly extracted source
        """

        data = {'description': "monitoringlist:" + self._testMethodName}
        dataset = DataSet(data=data)

        # Three timesteps, 1 band -> 3 images.
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1),
                        datetime.datetime(2013, 10, 1)]
        #freq_effs = [124, 149, 156, 185]
        freq_effs = [124]
        freq_effs = [f * 1e6 for f in freq_effs]

        im_params = db_subs.generate_timespaced_dbimages_data(len(freq_effs)
                                                     * len(taustart_tss))
        timestamps = itertools.repeat(taustart_tss, len(freq_effs))

        for im, freq, ts in zip(im_params, itertools.cycle(freq_effs),
                                itertools.chain.from_iterable(zip(*timestamps))):
            im['freq_eff'] = freq
            im['taustart_ts'] = ts

        images = []
        for im in im_params:
            image = tkp.db.Image(dataset=dataset, data=im)
            images.append(image)

        # Arbitrary parameters, except that they fall inside our image.
        # We have one to be monitored source and one "normal" source
        src0 = db_subs.example_extractedsource_tuple(ra=122.5, dec=9.5)
        src1_mon = db_subs.example_extractedsource_tuple(ra=122.5, dec=9.5)

        # Group images in blocks of 1, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # The "normal" source is seen at all timesteps
                dbgen.insert_extracted_sources(image.id, [src0], 'blind')

            for image in images:
                associate_extracted_sources(image.id, deRuiter_r=5.68)
                # The monitoring sources are the positional inputs for the forced
                # fits, which on their turn return additional parameters,
                # e.g. from src0_mon
                # src1_mon is the monitoring source at all timesteps
                dbgen.insert_extracted_sources(image.id, [src1_mon], 'ff_ms')

                # And here we have to associate the monitoring sources with the
                # runcat sources...
                dbmon.associate_ms(image.id)

        query = """\
        SELECT id
              ,mon_src
          FROM runningcatalog r
         WHERE dataset = %(dataset_id)s
           AND datapoints = 3
        ORDER BY id
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog sources, one for the "normal"
        # source and one for the monitoring source.
        # Both should have three datapoints.
        print "dp_result:",result
        self.assertEqual(len(result), 2)
        # The first source is the "normal" one
        self.assertEqual(result[0][1], False)
        # The second source is the monitoring one
        self.assertEqual(result[1][1], True)

        query = """\
        SELECT r.id
              ,r.mon_src
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset_id)s
           AND rf.runcat = r.id
        ORDER BY r.id
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog_flux entries,
        # one for every source, where every source has
        # three f_datapoints
        self.assertEqual(len(result), 2)

        # "Normal" source: three flux datapoints
        self.assertEqual(result[0][1], False)
        self.assertEqual(result[0][2], 3)
        # Monitoring source: three flux datapoints
        self.assertEqual(result[1][1], True)
        self.assertEqual(result[1][2], 3)

        # We should also have two lightcurves for both sources,
        # where both sources have three datapoints.
        # The association types of the "normal" source are
        # 3 (first) or 4 (later ones), while the monitoring source
        # association types are 8 (first) or 9 (later ones).
        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.type
              ,i.taustart_ts
              ,r.mon_src
              ,x.extract_type
          FROM assocxtrsource a
              ,extractedsource x
              ,image i
              ,runningcatalog r
         WHERE a.xtrsrc = x.id
           AND x.image = i.id
           AND i.dataset = %(dataset_id)s
           AND a.runcat = r.id
        ORDER BY a.runcat
                ,i.taustart_ts
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # 3 + 3 entries for source 1 and 2 resp.
        self.assertEqual(len(result), 6)

        # The individual light-curve datapoints for the "normal" source
        # It was new at first timestep
        self.assertEqual(result[0][2], 4)
        self.assertEqual(result[0][3], taustart_tss[0])
        self.assertEqual(result[0][4], False)
        self.assertEqual(result[0][5], 0)

        # It was known at second timestep
        self.assertEqual(result[1][2], 3)
        self.assertEqual(result[1][3], taustart_tss[1])
        self.assertEqual(result[1][4], result[0][4])
        self.assertEqual(result[1][5], result[0][5])

        # It was known at third timestep
        self.assertEqual(result[2][2], result[1][2])
        self.assertEqual(result[2][3], taustart_tss[2])
        self.assertEqual(result[2][4], result[1][4])
        self.assertEqual(result[2][5], result[1][5])

        # The individual light-curve datapoints for the monitoring source
        # It was new at first timestep
        self.assertEqual(result[3][2], 8)
        self.assertEqual(result[3][3], taustart_tss[0])
        self.assertEqual(result[3][4], True)
        self.assertEqual(result[3][5], 2)

        # It was known at second timestep
        self.assertEqual(result[4][2], 9)
        self.assertEqual(result[4][3], taustart_tss[1])
        self.assertEqual(result[4][4], result[3][4])
        self.assertEqual(result[4][5], result[3][5])

        # It was known at third timestep
        self.assertEqual(result[5][2], result[4][2])
        self.assertEqual(result[5][3], taustart_tss[2])
        self.assertEqual(result[5][4], result[4][4])
        self.assertEqual(result[5][5], result[4][5])

