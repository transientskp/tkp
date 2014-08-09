import datetime
import itertools
from collections import defaultdict
import unittest

import tkp.db
from tkp.db import associations as dbass
from tkp.db import general as dbgen
from tkp.db.nulldetections import get_nulldetections
from tkp.db import monitoringlist as dbmon
from tkp.db.orm import DataSet
from tkp.db.generic import columns_from_table, get_db_rows_as_dicts
from tkp.testutil import db_subs
from tkp.testutil.db_queries import get_assoc_entries
from tkp.testutil.decorators import requires_database

# Use a default argument value for convenience
from functools import partial
associate_extracted_sources = partial(dbass.associate_extracted_sources,
                                      new_source_sigma_margin=3)

@requires_database()
class TestInsert(unittest.TestCase):
    """
    A quick sanity check
    """
    def setUp(self):
        self.description = {'description':
                                "monitoringlist:" + self._testMethodName}

    def tearDown(self):
        tkp.db.rollback()

    def test_insert(self):
        dataset1 = DataSet(data=self.description)
        monitor_positions = [ (5., 5), (123,85.)]
        dbgen.insert_monitor_positions(dataset1.id, monitor_positions)


@requires_database()
class TestMonitor(unittest.TestCase):
    """
    These tests will check that monitoringlist sources are associated only amongst themselves.
    """
    def shortDescription(self):
        """http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/"""
        return None

    def setUp(self):
        data = {'description': "monitoringlist:" + self._testMethodName}
        self.dataset = DataSet(data=data)
        self.im_params = db_subs.generate_timespaced_dbimages_data(n_images=3)
    def tearDown(self):
        tkp.db.rollback()

    def test_basic_case(self):
        im_params = self.im_params

        blind_src = db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             )
        superimposed_mon_src = blind_src
        mon_src_in_field = blind_src._replace(ra = blind_src.ra+0.001)
        # Simulate a source that does not get fit, for good measure:
        mon_src_out_of_field = blind_src._replace(ra = blind_src.ra+90.)

        #Sorted by increasing RA:
        mon_srcs = [superimposed_mon_src, mon_src_in_field, mon_src_out_of_field]
        mon_posns = [(m.ra, m.dec) for m in mon_srcs]
        dbgen.insert_monitor_positions(self.dataset.id,mon_posns)

        images = []
        for img_pars in self.im_params:
            img = tkp.db.Image(dataset=self.dataset, data=img_pars)
            dbgen.insert_extracted_sources(img.id, [blind_src], 'blind')
            associate_extracted_sources(img.id, deRuiter_r=5.68)
            nd_requests = get_nulldetections(img.id)
            self.assertEqual(len(nd_requests),0)
            mon_requests = dbmon.get_monitor_entries(self.dataset.id)
            self.assertEqual(len(mon_requests),len(mon_srcs))
            # mon requests is a list of tuples [(id,ra,decl)]
            # Ensure sorted by RA for cross-checking:
            mon_requests = sorted(mon_requests, key = lambda s: s[1])

            for idx in range(len(mon_srcs)):
                self.assertAlmostEqual(mon_requests[idx][1],mon_srcs[idx].ra)
                self.assertAlmostEqual(mon_requests[idx][2],mon_srcs[idx].dec)

            #Insert fits for the in-field sources and then associate
            dbgen.insert_extracted_sources(img.id,
                       [superimposed_mon_src, mon_src_in_field], 'ff_ms',
                       ff_monitor_ids=[mon_requests[0][0],
                                       mon_requests[1][0]])
            dbmon.associate_ms(img.id)

        query = """\
        SELECT r.id
              ,r.mon_src
              ,rf.f_datapoints
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset_id)s
           AND rf.runcat = r.id
        ORDER BY r.wm_ra
                ,r.mon_src
        """
        cursor = tkp.db.execute(query, {'dataset_id': self.dataset.id})
        runcat_flux = get_db_rows_as_dicts(cursor)


        self.assertEqual(len(runcat_flux), 3)
        # First entry (lowest RA, mon_src = False) is the regular one;
        self.assertEqual(runcat_flux[0]['mon_src'], False)
        # The higher RA source is the monitoring one
        self.assertEqual(runcat_flux[1]['mon_src'], True)
        self.assertEqual(runcat_flux[2]['mon_src'], True)

        for entry in runcat_flux:
            self.assertEqual(entry['f_datapoints'], len(self.im_params))



        #Let's verify the association types
        blind_src_assocs = get_assoc_entries(self.dataset.database,
                                             runcat_flux[0]['id'])

        superimposed_mon_src_assocs = get_assoc_entries(self.dataset.database,
                                             runcat_flux[1]['id'])
        offset_mon_src_assocs = get_assoc_entries(self.dataset.database,
                                             runcat_flux[2]['id'])

        assoc_lists = [blind_src_assocs,
                       superimposed_mon_src_assocs,
                       offset_mon_src_assocs]

        for al in assoc_lists:
            self.assertEqual(len(al), 3)


        # The individual light-curve datapoints for the "normal" source
        # It was new at first timestep
        self.assertEqual(blind_src_assocs[0]['type'], 4)
        self.assertEqual(superimposed_mon_src_assocs[0]['type'], 8)
        self.assertEqual(offset_mon_src_assocs[0]['type'], 8)

        for idx, img_pars in enumerate(self.im_params):
            if idx != 0:
                self.assertEqual(blind_src_assocs[idx]['type'], 3)
                self.assertEqual(superimposed_mon_src_assocs[idx]['type'], 9)
                self.assertEqual(offset_mon_src_assocs[idx]['type'], 9)

            #And the extraction types:
            self.assertEqual(blind_src_assocs[idx]['extract_type'],0)
            self.assertEqual(superimposed_mon_src_assocs[idx]['extract_type'],2)
            self.assertEqual(offset_mon_src_assocs[idx]['extract_type'],2)

            #Sanity check the timestamps while we're at it
            for al in assoc_lists:
                self.assertEqual(al[idx]['taustart_ts'],
                             img_pars['taustart_ts'])

