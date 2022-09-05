from builtins import range
from operator import attrgetter
import unittest
import datetime
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs
from tkp.testutil import db_queries
from tkp.db.orm import DataSet
from tkp.db.orm import Image
import tkp.db
from tkp.db.associations import associate_extracted_sources
from tkp.db.general import insert_extracted_sources
from tkp.db.general import lightcurve as ligtcurve_func
from tkp.db.generic import get_db_rows_as_dicts, columns_from_table


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
        image_datasets = db_subs.generate_timespaced_dbimages_data(n_images=4,
            taustart_ts= datetime.datetime(2010, 3, 3)
        )

        for dset in image_datasets:
            image = Image(dataset=self.dataset, data=dset)
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
            insert_extracted_sources(image._id, img_sources)
            associate_extracted_sources(image._id, deRuiter_r=3.7,
                                        new_source_sigma_margin=3)

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
        lightcurve = ligtcurve_func(sources[0]._id)

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
            for key in list(flux_summary.keys()):
                self.assertAlmostEqual(flux_summary[key], py_results[-1][key])

        #Now check the per-timestep statistics (variability indices)
        sorted_runcat_ids = columns_from_table('runningcatalog',
                                               where={'dataset':self.dataset.id},
                                               order='wm_ra')
        sorted_runcat_ids = [entry['id'] for entry in sorted_runcat_ids]

        for idx, rcid in enumerate(sorted_runcat_ids):
            db_indices = db_queries.get_assoc_entries(self.database,
                                                                   rcid)
            py_indices = db_subs.lightcurve_metrics(lightcurves_sorted_by_ra[idx])
            self.assertEqual(len(db_indices), len(py_indices))
            for nstep in range(len(db_indices)):
                for key in ('v_int', 'eta_int', 'f_datapoints'):
                    self.assertAlmostEqual(db_indices[nstep][key],
                                           py_indices[nstep][key],
                                           places=5)

