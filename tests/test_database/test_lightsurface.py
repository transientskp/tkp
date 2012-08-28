
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
import tkp.database
import datetime
from operator import attrgetter


class TestLightSurface(unittest.TestCase):
    def setUp(self):
        import tkp.database
        self.database = tkp.database.DataBase()
        self.dataset = DataSet(data={'description': 'dataset with images'}, database=self.database)

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_lightsurface(self):
        images = []
        # make 4 * 5 images with different frequencies and date
        for frequency in [80e6, 90e6, 100e6, 110e6, 120e6]:
            for day in [3, 4, 5, 6]:
                data = {'taustart_ts': datetime.datetime(2010, 3, day),
                        'tau_time': 3600,
                        'url': '/',
                        'freq_eff': frequency,
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
            sources = []
            for data in data_list:
                source = (data['ra'], data['decl'],
                          data['ra_err'], data['decl_err'],
                          data['i_peak']*(1+i), data['i_peak_err'],
                          data['i_peak']*(1+i), data['i_peak_err'],
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

        # TODO: aaarch this is so ugly. Because this a set we need to pop it.
        sources = self.dataset.images.pop().sources
        #sources = self.dataset.images[-1].sources

        sources = sorted(sources, key=attrgetter('ra'))
        extracted_source = sources[0].id
        lightcurve = tkp.database.utils.general.lightcurve(self.database.connection, extracted_source)

        # check if a lightcurve only contains sources for one frequency
        # TODO: ok this is not good, a lightcurve contains points from all frequencies now
        #self.assertEqual(len(images), len(lightcurve))

        #lightsurface = tkp.database.utils.general.lightsurface(self.database.connection, extracted_source)


if __name__ == '__main__':
    unittest.main()
