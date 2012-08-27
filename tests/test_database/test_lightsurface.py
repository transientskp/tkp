
import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_subs
from decorators import requires_database
from tkp.database.orm import DataSet
from tkp.database.orm import Image
import datetime
from operator import attrgetter, itemgetter


class TestLightSurface(unittest.TestCase):
    def setUp(self):
        import tkp.database
        self.database = tkp.database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_lightsurface(self):
        dataset = DataSet(data={'description': 'dataset with images'}, database=self.database)

        images = []
        # make 4 * 5 images with different frequencies and date
        for frequency in [80e6, 90e6, 100e6, 110e6, 120e6]:
            for day in [3, 4, 5, 6]:
                data = {'taustart_ts': datetime.datetime(2010, 3, day),
                        'tau_time': 3600,
                        'url': '/',
                        'freq_eff': frequency,
                        'freq_bw': 1e6}
                image = Image(dataset=dataset, data=data)
                images.append(image)

        # 3 sources per image, with different coordinates & flux
        data_list = [dict(ra=111.111*i, decl=11.11*i,
            ra_err=0.01, decl_err=0.01,
            i_peak=10*i, i_peak_err=0.1,
            #                          x=0.11, y=0.22, z=0.33, det_sigma=11.1,
            #                          zone=i
        )
                     for i in range(1, 4)]
        # Insert the 3 sources in each image, while further varying the flux
        for i, image in enumerate(images):
            # Create the "source finding results"
            sources = [
            (data['ra'], data['decl'],
             data['ra_err'], data['decl_err'],
             data['i_peak']*(1+i), data['i_peak_err'],
             data['i_peak']*(1+i), data['i_peak_err'],
             10.,#Significance level
             1, 1, 0) #Beam params (width arcsec major, width arcsec minor, parallactic angle)
                      for data in data_list]
            # Insert the sources
            image.insert_extracted_sources(sources)
            # Run the association for each list of source for an image
            image.associate_extracted_sources()

        # updates the dataset and its set of images
        dataset.update()
        dataset.update_images()

        # update the images and their sets of sources
        for image in dataset.images:
            image.update()
            image.update_sources()

        # Now pick any image, select the first source (smallest RA)
        # and extract its light curve
        sources = dataset.images.pop().sources
        sources = sorted(sources, key=attrgetter('ra'))
        lightcurve = sources[0].lightcurve()
        self.assertEqual(lightcurve[0][0], datetime.datetime(2010, 3, 3, 0, 0))
        self.assertEqual(lightcurve[1][0], datetime.datetime(2010, 3, 4, 0, 0))
        self.assertEqual(lightcurve[2][0], datetime.datetime(2010, 3, 5, 0, 0))
        self.assertEqual(lightcurve[3][0], datetime.datetime(2010, 3, 6, 0, 0))
        self.assertAlmostEqual(lightcurve[0][2], 10.)
        self.assertAlmostEqual(lightcurve[1][2], 20.)
        self.assertAlmostEqual(lightcurve[2][2], 30.)
        self.assertAlmostEqual(lightcurve[3][2], 40.)

        # Since the light curves are very similar, only eta_nu is different
        results = dataset.detect_variables()
        results = sorted(results, key=itemgetter('eta_nu'))
        for result, eta_nu in zip(results, (16666.66666667, 66666.666666667, 150000.0)):
            self.assertEqual(result['npoints'], 4)
            self.assertAlmostEqual(result['eta_nu'], eta_nu)
            self.assertAlmostEqual(result['v_nu'], 0.516397779494)

    
