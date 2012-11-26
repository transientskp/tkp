
import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import tkp.testutil.db_subs
from tkp.testutil.decorators import requires_database
from tkp.database.orm import DataSet
from tkp.database.orm import Image
import tkp.database
import datetime
from operator import attrgetter, itemgetter

class TestLightCurve(unittest.TestCase):
    def setUp(self):
        self.database = tkp.database.DataBase()
        self.dataset = DataSet(data={'description': 'dataset with images'}, database=self.database)
    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_lightcurve(self):
        # make 4 * 5 images with different date
        images = []
        for day in [3, 4, 5, 6]:
            data = {'taustart_ts': datetime.datetime(2010, 3, day),
                    'tau_time': 3600,
                    'url': '/',
                    'freq_eff': 80e6,
                    'freq_bw': 1e6}
            image = Image(dataset=self.dataset, data=data)
            images.append(image)

        # 3 sources per image, with different coordinates & flux
        data_list = []
        for i in range(1, 4):
            data_list.append({
                'ra': 111.111*i,
                'decl': 11.11*i,
                'ra_err': 0.01,
                'decl_err': 0.01,
                'i_peak': 10*i,
                'i_peak_err': 0.1,
            #  x=0.11, y=0.22, z=0.33, det_sigma=11.1, zone=i
            })

        # Insert the 3 sources in each image, while further varying the flux
        for i, image in enumerate(images):
            # Create the "source finding results"
            # Note that we reuse 'i_peak' as both peak & integrated flux.
            sources = []
            for data in data_list:
                source = (data['ra'], data['decl'],
                     data['ra_err'], data['decl_err'],
                     data['i_peak']*(1+i), data['i_peak_err'], # Peak
                     data['i_peak']*(1+i), data['i_peak_err'], # Integrated
                     10., # Significance level
                     1, 1, 0) # Beam params (width arcsec major, width arcsec minor, parallactic angle)
                sources.append(source)

            # Insert the sources
            image.insert_extracted_sources(sources)

            # Run the association for each list of source for an image
            image.associate_extracted_sources()

        # updates the dataset and its set of images
        self.dataset.update()
        self.dataset.update_images()

        # update the images and their sets of sources
        for image in self.dataset.images:
            image.update()
            image.update_sources()
            # Now pick any image, select the first source (smallest RA)

        # and extract its light curve
        sources = self.dataset.images.pop().sources
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
        results = self.dataset.detect_variables(
                                            self.dataset.frequency_bands()[0])
        results = sorted(results, key=itemgetter('eta_int'))
        for result, eta_nu in zip(results, (16666.66666667, 66666.666666667,
                                            150000.0)):
            self.assertEqual(result['npoints'], 4)
            self.assertAlmostEqual(result['eta_int'], eta_nu)
            self.assertAlmostEqual(result['v_int'], 0.516397779494)

    
