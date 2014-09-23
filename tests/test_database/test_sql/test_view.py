import unittest
import tkp.db
from tkp.testutil import db_subs


class TestAugmentedRunningcatalog(unittest.TestCase):
    def setUp(self):
        """
        create a fake transient. Taken from the transient test.
        :return:
        """
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(data={'description':
                                                "Augmented Runningcatalog test"},
                                      database=self.database)

        self.n_images = 4
        self.new_source_sigma_margin = 3
        image_rms = 1e-3
        detection_thresh = 10

        self.search_params = {'eta_min': 1, 'v_min': 0.1}

        self.barely_detectable_flux = 1.01 * image_rms * detection_thresh
        self.reliably_detectable_flux = 1.01 * image_rms * (detection_thresh +
                                                            self.new_source_sigma_margin)

        # 1mJy image RMS, 10-sigma detection threshold = 10mJy threshold.
        test_specific_img_params = {'rms_qc': image_rms, 'rms_min': image_rms,
                                    'rms_max': image_rms,
                                    'detection_thresh': detection_thresh}

        self.im_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)

        im_params = self.im_params
        src_tuple = db_subs.example_extractedsource_tuple(ra=im_params[0]['centre_ra'],
                                                          dec=im_params[0]['centre_decl'],)
        transient_src = db_subs.MockSource(
            template_extractedsource=src_tuple,
            lightcurve={im_params[2]['taustart_ts']:
                            self.reliably_detectable_flux}
        )

        for img_pars in im_params:
            db_subs.insert_image_and_simulated_sources(self.dataset, img_pars,
                                                       [transient_src],
                                                       self.new_source_sigma_margin)

    def tearDown(self):
        tkp.db.rollback()

    def test_extra_columns(self):
        query = """
        SELECT
            v_int, eta_int, sigma_max, sigma_min, lightcurve_max, lightcurve_avg
        FROM
            augmented_runningcatalog
        WHERE
            dataset = %s
        ORDER BY
            id
        """ % self.dataset.id

        cursor = tkp.db.execute(query)
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        v_int, eta_int, sigma_max, sigma_min, lightcurve_max, lightcurve_avg = rows[0]
        self.assertAlmostEqual(v_int, 1.41421356237309)
        self.assertAlmostEqual(eta_int, 344.7938)
        self.assertAlmostEqual(sigma_max, 13.13)
        self.assertAlmostEqual(sigma_min, 13.13)
        self.assertAlmostEqual(lightcurve_max, 0.01313)
        self.assertAlmostEqual(lightcurve_avg, 0.006565)

    def test_count(self):
        """
        make sure the augmented view has the same row count as the runcat table
        """
        q1 = "select count(id) from runningcatalog"
        q2 = "select count(id) from augmented_runningcatalog"

        r1 = tkp.db.execute(q1).fetchall()[0][0]
        r2 = tkp.db.execute(q2).fetchall()[0][0]

        self.assertEqual(r1, r2)