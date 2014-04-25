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

        # Arbitrary parameters, except that they fall insite our image.
        src0 = db_subs.example_extractedsource_tuple(ra=122.5, dec=9.5)
        src1 = db_subs.example_extractedsource_tuple(ra=123.5, dec=10.5)

        # Group images in blocks of 4, corresponding to all frequency bands at
        # a given timestep.
        for images in zip(*(iter(images),) * len(freq_effs)):
            for image in images:
                # The first source is only seen at timestep 0, band 0.
                # The second source is only seen at timestep 1, band 3.
                if (image.taustart_ts == taustart_tss[0] and image.freq_eff == freq_effs[0]):
                    dbgen.insert_extracted_sources(image.id, [src0], 'blind')
                elif (image.taustart_ts == taustart_tss[1] and image.freq_eff == freq_effs[3]):
                    dbgen.insert_extracted_sources(image.id, [src1], 'blind')
                else:
                    pass

            for image in images:
                null_detections = dbmon.get_nulldetections(image.id, 5.68)
                if (image.taustart_ts == taustart_tss[0]):
                    # There are no null detections at the first timestep
                    self.assertEqual(len(null_detections), 0)
                elif image.taustart_ts == taustart_tss[1]:
                    # src0 is a null detection at the second timestep
                    self.assertEqual(len(null_detections), 1)
                    dbgen.insert_extracted_sources(image.id, [src0], 'ff_nd')
                else:
                    # All other images have two null detections.
                    self.assertEqual(len(null_detections), 2)
                    dbgen.insert_extracted_sources(image.id, [src0, src1], 'ff_nd')
                dbass.associate_extracted_sources(image.id, deRuiter_r=5.68)

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

        # Inserted into timestep 2. Seen in one image there, and force-fits in
        # all four images at timestep 3.
        self.assertEqual(result[0][1], 5)

        # Inserted into timestep 1. Seen in one image there, and force-fits in
        # all eight images at timesteps 2 and 3.
        self.assertEqual(result[1][1], 9)
