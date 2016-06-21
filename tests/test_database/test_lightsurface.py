from operator import attrgetter

import unittest

import datetime
from tkp.testutil.decorators import requires_database
from tkp.db.orm import DataSet
from tkp.db.orm import Image
from tkp.db.associations import associate_extracted_sources
from tkp.db.general import insert_extracted_sources
import tkp.db
from tkp.testutil import db_subs


class TestLightSurface(unittest.TestCase):
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = DataSet(data={'description': 'dataset with images'})

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_lightsurface(self):
        images = []
        # make 4 * 5 images with different frequencies and date
        for frequency in [80e6, 90e6, 100e6, 110e6, 120e6]:
            for day in [3, 4, 5, 6]:
                img_data = db_subs.example_dbimage_data_dict(
                    taustart_ts=datetime.datetime(2010, 3, day),
                    freq_eff = frequency
                )
                image = Image(dataset=self.dataset, data=img_data)
                images.append(image)

        # 3 sources per image, with different coordinates & flux
        data_list = []
        for i in range(1, 4):
            data_list.append({
                'ra': 111.111 + i,
                'decl': 11.11 + i,
                'ra_fit_err': 0.01,
                'decl_fit_err': 0.01,
                'i_peak': 10.*i,
                'i_peak_err': 0.1,
                'error_radius': 10.0,
                'fit_type': 1,
                #  x=0.11, y=0.22, z=0.33, det_sigma=11.1, zone=i
            })

        # Insert the 3 sources in each image, while further varying the flux
        for i, image in enumerate(images):
            # Create the "source finding results"
            sources = []
            for data in data_list:
                source = db_subs.example_extractedsource_tuple(
                        ra=data['ra'], dec=data['decl'],
                        ra_fit_err=data['ra_fit_err'],
                        dec_fit_err= data['decl_fit_err'],
                        peak = data['i_peak']*(1+i),
                        peak_err = data['i_peak_err'],
                        flux = data['i_peak']*(1+i),
                        flux_err = data['i_peak_err'],
                        fit_type=data['fit_type']
                        )
                sources.append(source)

            # Insert the sources
            insert_extracted_sources(image._id, sources)

            # Run the association for each list of source for an image
            associate_extracted_sources(image._id, deRuiter_r=3.7,
                                        new_source_sigma_margin=3)

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
        lightcurve = tkp.db.general.lightcurve(extracted_source)

        # check if a lightcurve only contains sources for one frequency
        # TODO: ok this is not good, a lightcurve contains points from all frequencies now
        #self.assertEqual(len(images), len(lightcurve))

        #lightsurface = tkp.db.general.lightsurface(extracted_source)


if __name__ == '__main__':
    unittest.main()
