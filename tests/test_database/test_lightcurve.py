from operator import attrgetter, itemgetter
from collections import namedtuple

import unittest

import datetime
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_queries
from tkp.testutil import db_subs
from tkp.testutil import db_queries
from tkp.db.orm import DataSet
from tkp.db.orm import Image
import tkp.db
import tkp.db.transients as dbtransients
from tkp.db.generic import  get_db_rows_as_dicts, columns_from_table


class TestLightCurve(unittest.TestCase):
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = DataSet(data={'description': 'dataset with images'},
                               database=self.database)

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_lightcurve(self):
        # make 4 images with different date
        images = []
        for day in [3, 4, 5, 6]:
            data = {'taustart_ts': datetime.datetime(2010, 3, day),
                    'tau_time': 3600,
                    'url': '/',
                    'freq_eff': 80e6,
                    'freq_bw': 1e6,
                    'beam_smaj_pix': float(2.7),
                    'beam_smin_pix': float(2.3),
                    'beam_pa_rad': float(1.7),
                    'deltax': float(-0.01111),
                    'deltay': float(0.01111),
                    'centre_ra': 111,
                    'centre_decl': 11,
                    'xtr_radius': 3,
                    'rms': 1,
            }
            image = Image(dataset=self.dataset, data=data)
            images.append(image)

        # 3 sources per image, with different coordinates & flux
        data_list = []
        for i in range(1, 4):
            data_list.append({
                'ra': 111.11 + i,
                'decl': 11.11 + i,
                'i_peak': 10. * i ,
                'i_peak_err': 0.1,
            })
        # Insert the 3 sources in each image, while further varying the flux
        lightcurves_sorted_by_ra = [[],[],[]]
        for im_idx, image in enumerate(images):
            # Create the "source finding results"
            # Note that we reuse 'i_peak' as both peak & integrated flux.
            img_sources = []
            for src_idx, data in enumerate(data_list):
                src = db_subs.example_extractedsource_tuple(
                    ra = data['ra'],dec=data['decl'],
                    peak=data['i_peak']* (1 + im_idx),
                    flux = data['i_peak']* (1 + im_idx)
                )
                lightcurves_sorted_by_ra[src_idx].append(src)
                img_sources.append(src)
            image.insert_extracted_sources(img_sources)
            image.associate_extracted_sources(deRuiter_r=3.7)

        # updates the dataset and its set of images
        self.dataset.update()
        self.dataset.update_images()

        # update the images and their sets of sources
        for image in self.dataset.images:
            image.update()
            image.update_sources()

        # Now pick last image, select the first source (smallest RA)
        # and extract its light curve
        sources = self.dataset.images[-1].sources
        sources = sorted(sources, key=attrgetter('ra'))
        lightcurve = sources[0].lightcurve()

        # check if the sources are associated in all images
        self.assertEqual(len(images), len(lightcurve))
        self.assertEqual(lightcurve[0][0], datetime.datetime(2010, 3, 3, 0, 0))
        self.assertEqual(lightcurve[1][0], datetime.datetime(2010, 3, 4, 0, 0))
        self.assertEqual(lightcurve[2][0], datetime.datetime(2010, 3, 5, 0, 0))
        self.assertEqual(lightcurve[3][0], datetime.datetime(2010, 3, 6, 0, 0))
        self.assertAlmostEqual(lightcurve[0][2], 10.)
        self.assertAlmostEqual(lightcurve[1][2], 20.)
        self.assertAlmostEqual(lightcurve[2][2], 30.)
        self.assertAlmostEqual(lightcurve[3][2], 40.)

         #Check the summary statistics (avg flux, etc)
        query = """\
        SELECT rf.avg_f_int
              ,rf.avg_f_int_sq
              ,avg_weighted_f_int
              ,avg_f_int_weight
          FROM runningcatalog r
              ,runningcatalog_flux rf
         WHERE r.dataset = %(dataset)s
           AND r.id = rf.runcat
        ORDER BY r.wm_ra
        """
        self.database.cursor.execute(query, {'dataset': self.dataset.id})
        runcat_flux_entries = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(runcat_flux_entries), len(lightcurves_sorted_by_ra))
        for idx, flux_summary in enumerate(runcat_flux_entries):
            py_results = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            for key in flux_summary.keys():
                self.assertAlmostEqual(flux_summary[key], py_results[-1][key])

        #Now check the per-timestep statistics (variability indices)
        sorted_runcat_ids = columns_from_table('runningcatalog',
                                               where={'dataset':self.dataset.id},
                                               order='wm_ra')
        sorted_runcat_ids = [entry['id'] for entry in sorted_runcat_ids]

        for idx, rcid in enumerate(sorted_runcat_ids):
            db_indices = db_queries.per_timestep_variability_indices(self.database,
                                                                   rcid)
            py_indices = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            self.assertEqual(len(db_indices), len(py_indices))
            for nstep in range(len(db_indices)):
                for key in ('v_int', 'eta_int'):
                    self.assertAlmostEqual(db_indices[nstep][key],
                                           py_indices[nstep][key],
                                           places=5)

