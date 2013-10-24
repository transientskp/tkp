import datetime
import itertools

import unittest2 as unittest

import tkp.db
from tkp.db import associations as dbass
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
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
        dataset = DataSet(data={'description': "null detection:" + self._testMethodName})

        # Three timesteps, each with 4 bands -> 12 images.
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1),
                        datetime.datetime(2013, 10, 1)]
        freq_effs = [124, 149, 156, 185]
        freq_effs = [f * 1e6 for f in freq_effs]

        im_params = db_subs.example_dbimage_datasets(len(freq_effs) * len(taustart_tss))
        timestamps = itertools.repeat(taustart_tss, len(freq_effs))

        for im, freq, ts in zip(im_params, itertools.cycle(freq_effs),
            itertools.chain.from_iterable(zip(*timestamps))
        ):
            im['freq_eff'] = freq
            im['taustart_ts'] = ts

        images = []
        for im in im_params:
            image = tkp.db.Image(dataset=dataset, data=im)
            images.append(image)

        # Source properties are the same in every image
        src = db_subs.example_extractedsource_tuple()

        # group images in blocks of 4, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # We 'skip' a couple of images to simulate missed blind
                # detections.
                print image.id, image.taustart_ts, image.freq_eff, type(image.taustart_ts)
                if (
                    (image.taustart_ts == taustart_tss[1] and image.freq_eff == freq_effs[0]) or
                    (image.taustart_ts == taustart_tss[2] and image.freq_eff == freq_effs[2])
                ):
                    pass
                else:
                    dbgen.insert_extracted_sources(image.id, [src], 'blind')

            for image in images:
                # The images we skipped above will have null detections at the
                # source position; the others should have no null detections.
                null_detections = dbmon.get_nulldetections(image.id, 5.68)
                if (
                    (image.taustart_ts == taustart_tss[1] and image.freq_eff == freq_effs[0]) or
                    (image.taustart_ts == taustart_tss[2] and image.freq_eff == freq_effs[2])
                ):
                    self.assertEqual(null_detections[0][0], src.ra)
                    self.assertEqual(null_detections[0][1], src.dec)
                    dbgen.insert_extracted_sources(image.id, [src], 'ff_nd')
                else:
                    self.assertEqual(len(null_detections), 0)
                dbass.associate_extracted_sources(image.id, deRuiter_r=5.68)

        query = """\
        SELECT id
              ,datapoints
        FROM runningcatalog r
        WHERE dataset = %(dataset_id)s
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = cursor.fetchall()
        # We should have a single running catalog source
        self.assertEqual(len(result), 1)

        # With a datapoint for every image
        self.assertEqual(result[0][1], len(im_params))
