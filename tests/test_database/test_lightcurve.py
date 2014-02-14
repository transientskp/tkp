from operator import attrgetter, itemgetter
from collections import namedtuple

import unittest2 as unittest

import datetime
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_queries
from tkp.testutil import db_subs
from tkp.testutil import db_queries
from tkp.db.orm import DataSet
from tkp.db.orm import Image
import tkp.db
import tkp.db.transients as dbtransients


class TestLightCurve(unittest.TestCase):
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = DataSet(data={'description': 'dataset with images'},
                               database=self.database)

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_lightcurve(self):
        # make 4 * 5 images with different date
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
                    'xtr_radius' : 3
            }
            image = Image(dataset=self.dataset, data=data)
            images.append(image)

        # 3 sources per image, with different coordinates & flux
        data_list = []
        for i in range(1, 4):
            data_list.append({
                'ra': 111.11 + i,
                'decl': 11.11 + i,
                'ra_fit_err': 0.01,
                'decl_fit_err': 0.01,
                'ew_sys_err': 20.,
                'ns_sys_err': 20.,
                'i_peak': 10. * i ,
                'i_peak_err': 0.1,
                'error_radius': 10.0
            #  x=0.11, y=0.22, z=0.33, det_sigma=11.1, zone=i
            })
        # Insert the 3 sources in each image, while further varying the flux
        XtrSrc = namedtuple('XtrSrc',['flux','flux_err'])
        src_list = []
        for i, image in enumerate(images):
            # Create the "source finding results"
            # Note that we reuse 'i_peak' as both peak & integrated flux.
            sources = []
            for data in data_list:
                source = (data['ra'], data['decl'],
                     data['ra_fit_err'], data['decl_fit_err'],  # Gaussian fit errors
                     data['i_peak'] * (1 + i), data['i_peak_err'],  # Peak
                     data['i_peak'] * (1 + i), data['i_peak_err'],  # Integrated
                     10.,  # Significance level
                     1, 1,  0, # Beam params (width arcsec major, width arcsec minor, parallactic angle)
                     data['ew_sys_err'], data['ns_sys_err'],  # Systematic errors
                     data['error_radius'])
                sources.append(source)
                src_list.append(XtrSrc(*[source[4],source[5]]))

            # Insert the sources
            image.insert_extracted_sources(sources)

            # Run the association for each list of source for an image
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

        # Since the light curves are very similar, only eta_nu is different
        results = dbtransients._select_updated_variability_indices(self.dataset.images[-1].id)
        results = sorted(results, key=itemgetter('eta_int'))
        for result, eta_nu in zip(results, (16666.66666667, 66666.666666667,
                                            150000.0)):
            self.assertEqual(result['f_datapoints'], 4)
            self.assertAlmostEqual(result['eta_int'], eta_nu)
            self.assertAlmostEqual(result['v_int'], 0.516397779494)

        # Check individual datapoints and their indices
        res = db_queries.evolved_var_indices(self.database, self.dataset.id)
        self.assertNotEqual(len(res), 0)
        runcat = res[0]
        xtrsrc = res[1]
        v_int = res[2]
        eta_int = res[3]
        self.assertEqual(len(runcat), 12)
        print "src_list=",src_list
        for src in src_list:
            print src
        py_v1, py_eta1 = db_subs.var_indices([src_list[0],src_list[3],src_list[6],src_list[9]])
        py_v2, py_eta2 = db_subs.var_indices([src_list[1],src_list[4],src_list[7],src_list[10]])
        py_v3, py_eta3 = db_subs.var_indices([src_list[2],src_list[5],src_list[8],src_list[11]])

        # We group the tests per runcat source (3 in total),
        # and every runcat has 4 associations
        self.assertAlmostEqual(v_int[0], py_v1[0])
        self.assertAlmostEqual(eta_int[0], py_eta1[0])
        self.assertAlmostEqual(v_int[1], py_v1[1])
        self.assertAlmostEqual(eta_int[1], py_eta1[1])
        self.assertAlmostEqual(v_int[2], py_v1[2])
        self.assertAlmostEqual(eta_int[2], py_eta1[2])
        self.assertAlmostEqual(v_int[3], py_v1[3])
        self.assertAlmostEqual(eta_int[3], py_eta1[3])

        self.assertAlmostEqual(v_int[4], py_v2[0])
        self.assertAlmostEqual(eta_int[4], py_eta2[0])
        self.assertAlmostEqual(v_int[5], py_v2[1])
        self.assertAlmostEqual(eta_int[5], py_eta2[1])
        self.assertAlmostEqual(v_int[6], py_v2[2])
        self.assertAlmostEqual(eta_int[6], py_eta2[2])
        self.assertAlmostEqual(v_int[7], py_v2[3])
        self.assertAlmostEqual(eta_int[7], py_eta2[3])

        self.assertAlmostEqual(v_int[8], py_v3[0])
        self.assertAlmostEqual(eta_int[8], py_eta3[0])
        self.assertAlmostEqual(v_int[9], py_v3[1])
        self.assertAlmostEqual(eta_int[9], py_eta3[1])
        self.assertAlmostEqual(v_int[10], py_v3[2])
        self.assertAlmostEqual(eta_int[10], py_eta3[2])
        self.assertAlmostEqual(v_int[11], py_v3[3])
        self.assertAlmostEqual(eta_int[11], py_eta3[3])
