import datetime
import itertools

import unittest

import tkp.db
from tkp.db import associations as dbass
from tkp.db import general as dbgen
from tkp.db import nulldetections as dbnd
from tkp.db.orm import DataSet
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database


@requires_database()
class TestForcedFit(unittest.TestCase):
    """
    These tests will check whether null detections are picked up across bands
    """
    def shortDescription(self):
        """http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/"""
        return None

    def tearDown(self):
        tkp.db.rollback()

    def test_nullDetection(self):
        data = {'description': "null detection:" + self._testMethodName}
        dataset = DataSet(data=data)

        # Three timesteps, each with 4 bands -> 12 images.
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1),
                        datetime.datetime(2013, 10, 1)]
        freq_effs = [124, 149, 156, 185]
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
        src0 = db_subs.example_extractedsource_tuple(ra=122.5, dec=9.5)
        src1 = db_subs.example_extractedsource_tuple(ra=123.5, dec=10.5)

        # Group images in blocks of 4, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # The first source is only seen at timestep 0, band 0.
                # The second source is only seen at timestep 1, band 3.
                if (image.taustart_ts == taustart_tss[0] and
                            image.freq_eff == freq_effs[0]):
                    dbgen.insert_extracted_sources(image.id, [src0], 'blind')
                elif (image.taustart_ts == taustart_tss[1] and
                      image.freq_eff == freq_effs[3]):
                    dbgen.insert_extracted_sources(image.id, [src1], 'blind')
                else:
                    pass

            for image in images:
                dbass.associate_extracted_sources(image.id, deRuiter_r=5.68,
                                                  new_source_sigma_margin=3)
                nd_ids_pos = dbnd.get_nulldetections(image.id)
                # The null_detections are the positional inputs for the forced
                # fits, which on their turn return additional parameters,
                # e.g. from src0, src1
                if image.taustart_ts == taustart_tss[0]:
                    # There are no null detections at the first timestep
                    self.assertEqual(len(nd_ids_pos), 0)
                elif image.taustart_ts == taustart_tss[1]:
                    # src0 is a null detection at the second timestep
                    self.assertEqual(len(nd_ids_pos), 1)
                    dbgen.insert_extracted_sources(image.id, [src0], 'ff_nd',
                           ff_runcatids=[ids for ids, ra, decl in nd_ids_pos])
                else:
                    # All other images have two null detections.
                    self.assertEqual(len(nd_ids_pos), 2)
                    dbgen.insert_extracted_sources(image.id, [src0, src1],
                                                   'ff_nd',
                           ff_runcatids=[ids for ids, ra, decl in nd_ids_pos])

                # And here we have to associate the null detections with the
                # runcat sources...
                dbnd.associate_nd(image.id)

        query = """\
        SELECT id
              ,datapoints
        FROM runningcatalog r
        WHERE dataset = %(dataset_id)s
        ORDER BY datapoints
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog sources, with a datapoint for
        # every image in which the sources were seen.
        self.assertEqual(len(result), 2)

        query = """\
        SELECT r.id
              ,rf.band
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset_id)s
           AND rf.runcat = r.id
        ORDER BY r.id
                ,rf.band
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have eight runningcatalog_flux entries,
        # one for every source in every band, i.e. 2 x 4.
        # The number of flux datapoints differ per source, though
        self.assertEqual(len(result), 8)

        # Source 1: inserted into timestep 0, band 0.
        # Force-fits in band 0 images at next timesteps,
        # so 1+2 for band 0.
        self.assertEqual(result[0][2], 3)

        # Source 1: inserted into timestep 0, band 0.
        # Force-fits in bands 1,2,3 images at next timesteps.
        # so 0+2 for bands 1,2,3.
        self.assertEqual(result[1][2], 2)
        self.assertEqual(result[2][2], 2)
        self.assertEqual(result[3][2], 2)

        # Source 2: inserted into timestep 1, band 3.
        # Force-fits in band 0,1,2 images at next timestep,
        # so 1 for band 0,1,2
        self.assertEqual(result[4][2], 1)
        self.assertEqual(result[5][2], 1)
        self.assertEqual(result[6][2], 1)

        # Source 2: inserted into timestep 1, band 3.
        # Force-fit in band 3 image at next timestep,
        # so 1+1 for band 3
        self.assertEqual(result[7][2], 2)

        # We should also have two lightcurves for both sources,
        # where source 1 has 3 datapoints in band0 (t1,t2,t3)
        # and 2 datapoints for the other three bands (t2,t3).
        # Source 2 has two datapoints for band3 (t2,t3) and
        # one for the other three bands (t3).
        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.type
              ,i.band
              ,i.taustart_ts
          FROM assocxtrsource a
              ,extractedsource x
              ,image i
         WHERE a.xtrsrc = x.id
           AND x.image = i.id
           AND i.dataset = %(dataset_id)s
        ORDER BY a.runcat
                ,i.band
                ,i.taustart_ts
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # 9 + 5 entries for source 1 and 2 resp.
        self.assertEqual(len(result), 14)

        # The individual light-curve datapoints
        # Source1: new at t1, band0
        self.assertEqual(result[0][2], 4)
        self.assertEqual(result[0][4], taustart_tss[0])

        # Source1: Forced fit at t2, same band
        self.assertEqual(result[1][2], 7)
        self.assertEqual(result[1][3], result[0][3])
        self.assertEqual(result[1][4], taustart_tss[1])

        # Source1: Forced fit at t3, same band
        self.assertEqual(result[2][2], 7)
        self.assertEqual(result[2][3], result[1][3])
        self.assertEqual(result[2][4], taustart_tss[2])

        # Source1: Forced fit at t2, band1
        self.assertEqual(result[3][2], 7)
        self.assertTrue(result[3][3] > result[2][3])
        self.assertEqual(result[3][4], taustart_tss[1])

        # Source1: Forced fit at t3, band1
        self.assertEqual(result[4][2], 7)
        self.assertEqual(result[4][3], result[3][3])
        self.assertEqual(result[4][4], taustart_tss[2])

        # Source1: Forced fit at t2, band2
        self.assertEqual(result[5][2], 7)
        self.assertTrue(result[5][3] > result[4][3])
        self.assertEqual(result[5][4], taustart_tss[1])

        # Source1: Forced fit at t3, band2
        self.assertEqual(result[6][2], 7)
        self.assertEqual(result[6][3], result[5][3])
        self.assertEqual(result[6][4], taustart_tss[2])

        # Source1: Forced fit at t2, band3
        self.assertEqual(result[7][2], 7)
        self.assertTrue(result[7][3] > result[6][3])
        self.assertEqual(result[7][4], taustart_tss[1])

        # Source1: Forced fit at t3, band3
        self.assertEqual(result[8][2], 7)
        self.assertEqual(result[8][3], result[7][3])
        self.assertEqual(result[8][4], taustart_tss[2])

        # Source2: Forced fit at t3, band0
        self.assertEqual(result[9][2], 7)
        self.assertEqual(result[9][3], result[0][3])
        self.assertEqual(result[9][4], taustart_tss[2])

        # Source2: Forced fit at t3, band1
        self.assertEqual(result[10][2], 7)
        self.assertTrue(result[10][3] > result[9][3])
        self.assertEqual(result[10][4], taustart_tss[2])

        # Source2: Forced fit at t3, band2
        self.assertEqual(result[11][2], 7)
        self.assertTrue(result[11][3] > result[10][3])
        self.assertEqual(result[11][4], taustart_tss[2])

        # Source2: new at t2, band3
        self.assertEqual(result[12][2], 4)
        self.assertTrue(result[12][3] > result[11][3])
        self.assertEqual(result[12][4], taustart_tss[1])

        # Source2: Forced fit at t3, band3
        self.assertEqual(result[13][2], 7)
        self.assertEqual(result[13][3], result[12][3])
        self.assertEqual(result[13][4], taustart_tss[2])

    def test_1to1_nullDetection(self):
        """
        This tests that the two sources are associated if they were
        detected at different timesteps. The positions are used in
        the next test as well.
        """
        data = {'description': "null detection:" + self._testMethodName}
        dataset = DataSet(data=data)

        # Two timesteps, just 1 band -> 2 images.
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1)]
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

        # Arbitrary parameters, except that they fall inside our image
        # and close together (see next test)
        src0 = db_subs.example_extractedsource_tuple(ra=122.985, dec=10.5)
        src1 = db_subs.example_extractedsource_tuple(ra=123.015, dec=10.5)

        # Group images in blocks of 4, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # The sources are only seen at timestep 0
                if (image.taustart_ts == taustart_tss[0]):
                    dbgen.insert_extracted_sources(image.id, [src0], 'blind')
                elif (image.taustart_ts == taustart_tss[1]):
                    dbgen.insert_extracted_sources(image.id, [src1], 'blind')
                else:
                    pass

            for image in images:
                dbass.associate_extracted_sources(image.id, deRuiter_r=5.68,
                                                  new_source_sigma_margin=3)

        query = """\
        SELECT id
              ,datapoints
        FROM runningcatalog r
        WHERE dataset = %(dataset_id)s
        ORDER BY datapoints
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have one runningcatalog sources, with two datapoints
        # for the images in which the sources were seen.
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], 2)

        query = """\
        SELECT r.id
              ,rf.band
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset_id)s
           AND rf.runcat = r.id
        ORDER BY r.id
                ,rf.band
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have one runningcatalog_flux entry,
        # where the source has two flux datapoints
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], 2)


    def test_m2m_nullDetection(self):
        """
        This tests that two sources (close-by to be associated if they were
        detected at different timesteps) which are not seen in the next
        image and thus have forced fits, will have separate light curves.
        The postions are from the previous test.
        """
        data = {'description': "null detection:" + self._testMethodName}
        dataset = DataSet(data=data)

        # Three timesteps, just 1 band -> 3 images.
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1),
                        datetime.datetime(2013, 10, 1)]
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

        # Arbitrary parameters, except that they fall inside our image
        # and close together (see previous test)
        src0 = db_subs.example_extractedsource_tuple(ra=122.985, dec=10.5)
        src1 = db_subs.example_extractedsource_tuple(ra=123.015, dec=10.5)

        # Group images in blocks of 4, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # The sources are only seen at timestep 0
                if (image.taustart_ts == taustart_tss[0]):
                    dbgen.insert_extracted_sources(image.id, [src0,src1],
                                                   'blind')
                else:
                    pass

            for image in images:
                dbass.associate_extracted_sources(image.id, deRuiter_r=5.68,
                                                  new_source_sigma_margin=3)
                nd_ids_pos = dbnd.get_nulldetections(image.id)
                # The null_detections are the positional inputs for the forced
                # fits, which on their turn return additional parameters,
                # e.g. from src0, src1
                if image.taustart_ts == taustart_tss[0]:
                    # There are no null detections at the first timestep
                    self.assertEqual(len(nd_ids_pos), 0)
                elif image.taustart_ts == taustart_tss[1]:
                    # src0 & src1 are null detections at the second timestep
                    self.assertEqual(len(nd_ids_pos), 2)
                    dbgen.insert_extracted_sources(image.id, [src0,src1],
                                                   'ff_nd',
                          ff_runcatids=[ids for ids, ra, decl in nd_ids_pos])
                else:
                    # All other images have two null detections.
                    self.assertEqual(len(nd_ids_pos), 2)
                    dbgen.insert_extracted_sources(image.id, [src0, src1],
                                                   'ff_nd',
                          ff_runcatids=[ids for ids, ra, decl in nd_ids_pos])

                # And here we have to associate the null detections with the
                # runcat sources...
                if len(nd_ids_pos) > 0:
                    dbnd.associate_nd(image.id)

        query = """\
        SELECT id
              ,datapoints
        FROM runningcatalog r
        WHERE dataset = %(dataset_id)s
        ORDER BY datapoints
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog sources, with a datapoint for
        # every image in which the sources were seen.
        self.assertEqual(len(result), 2)

        query = """\
        SELECT r.id
              ,rf.band
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset_id)s
           AND rf.runcat = r.id
        ORDER BY r.id
                ,rf.band
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # We should have two runningcatalog_flux entries,
        # one for every source in the band, i.e. 2 x 1.
        self.assertEqual(len(result), 2)

        # Source 0: inserted into timestep 0.
        # Force-fits in images at next timesteps,
        # so 1+2 for band 0.
        self.assertEqual(result[0][2], 3)

        # Source 1: inserted into timestep 0
        # Force-fits in images at next timesteps.
        # so 1+2 for bands 0
        self.assertEqual(result[1][2], 3)
        #self.assertEqual(result[2][2], 2)
        #self.assertEqual(result[3][2], 2)

        # We should also have two lightcurves for both sources,
        # where source 1 has 3 datapoints in band0 (t1,t2,t3).
        # Source 2 also has 3 datapoints for band0 (t1,t2,t3).
        query = """\
        SELECT a.runcat
              ,a.xtrsrc
              ,a.type
              ,i.band
              ,i.taustart_ts
          FROM assocxtrsource a
              ,extractedsource x
              ,image i
         WHERE a.xtrsrc = x.id
           AND x.image = i.id
           AND i.dataset = %(dataset_id)s
        ORDER BY a.runcat
                ,i.band
                ,i.taustart_ts
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()

        # 3 + 3 entries for source 0 and 1 resp.
        self.assertEqual(len(result), 6)

        # The individual light-curve datapoints
        # Source1: new at t1, band0
        self.assertEqual(result[0][2], 4)
        self.assertEqual(result[0][4], taustart_tss[0])

        # Source1: Forced fit at t2, same band
        self.assertEqual(result[1][2], 7)
        self.assertEqual(result[1][3], result[0][3])
        self.assertEqual(result[1][4], taustart_tss[1])

        # Source1: Forced fit at t3, same band
        self.assertEqual(result[2][2], 7)
        self.assertEqual(result[2][3], result[1][3])
        self.assertEqual(result[2][4], taustart_tss[2])

        # Source2: new at t1, band0
        self.assertEqual(result[3][2], 4)
        self.assertEqual(result[3][3], result[1][3])
        self.assertEqual(result[3][4], taustart_tss[0])

        # Source2: Forced fit at t2, band0
        self.assertEqual(result[4][2], 7)
        self.assertEqual(result[4][3], result[3][3])
        self.assertEqual(result[4][4], taustart_tss[1])

        # Source2: Forced fit at t3, band0
        self.assertEqual(result[5][2], 7)
        self.assertEqual(result[5][3], result[4][3])
        self.assertEqual(result[5][4], taustart_tss[2])

