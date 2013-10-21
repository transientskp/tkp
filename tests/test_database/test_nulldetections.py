import math
import datetime
import logging

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
        # We have three timestamps of an image cube with 4 frfequency bands
        n_images = 12
        im_params = db_subs.example_dbimage_datasets(n_images)
        # Three timestamps
        taustart_tss = [datetime.datetime(2013, 8, 1),
                        datetime.datetime(2013, 9, 1), 
                        datetime.datetime(2013, 10, 1)]
        # Four frequencies/bands
        freq_effs = [124, 149, 156, 185]
        freq_effs[:] = [f * 1000000.0 for f in freq_effs]
        for idx, im in enumerate(im_params):
            print idx, idx%len(freq_effs), (idx - (idx%len(freq_effs)))/len(freq_effs)
            im['freq_eff'] = freq_effs[idx%len(freq_effs)]
            im['taustart_ts'] = taustart_tss[(idx - (idx%len(freq_effs)))/len(freq_effs)]

        images = []
        for im in im_params:
            print im
            image = tkp.db.Image(dataset=dataset, data=im)
            images.append(image)

        # Source properties are the same in every image
        src = db_subs.example_extractedsource_tuple()
        
        # group images by timestamp 
        grouped_images = [images[0:4], images[4:8], images[8:12]]
        for images in grouped_images:
            for image in images:
                print image.id, image.taustart_ts, image.freq_eff, type(image.taustart_ts)
                if ((image.taustart_ts == taustart_tss[1] and image.freq_eff == freq_effs[0])
                or (image.taustart_ts == taustart_tss[2] and image.freq_eff == freq_effs[2])): 
                    pass
                else:
                    dbgen.insert_extracted_sources(image.id, [src], 'blind')
            
            for image in images:
                null_detections = dbmon.get_nulldetections(image.id, 5.68) 
                print null_detections
                # image t2_b2 does not have detection, so there will be forced fit at 
                # the null_detection position
                if ((image.taustart_ts == taustart_tss[1] and image.freq_eff == freq_effs[0])
                or (image.taustart_ts == taustart_tss[2] and image.freq_eff == freq_effs[2])): 
                    self.assertEqual(null_detections[0][0], src.ra)
                    self.assertEqual(null_detections[0][1], src.dec)
                    dbgen.insert_extracted_sources(image.id, [src], 'ff_nd')
                dbass.associate_extracted_sources(image.id, deRuiter_r=5.68)

        query = """\
        SELECT id
              ,datapoints
          FROM runningcatalog r 
         WHERE dataset = %(dataset_id)s
        """
        cursor = tkp.db.execute(query, {'dataset_id': dataset.id})
        result = zip(*cursor.fetchall())
        self.assertNotEqual(len(result), 0)
        runcat = result[0]
        datapoints = result[1]

        self.assertEqual(len(runcat), 1)
        self.assertEqual(datapoints[0], n_images)

        #self.assertEqual(1,2)
