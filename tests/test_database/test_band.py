import unittest

import datetime
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs
import tkp.db
from tkp.db.orm import DataSet, Image
from tkp.db.database import Database
from copy import copy

class TestBand(unittest.TestCase):

    def setUp(self):
        import tkp.db.database
        self.database = tkp.db.database.Database()
        # Basic template data for each image.
        self.image_data = db_subs.example_dbimage_data_dict()

    def tearDown(self):
        tkp.db.rollback()

    @requires_database()
    def test_frequency_difference(self):
        # Check that images which are at almost the same fall nicely into the
        # same band (unless they fall over a band boundary). See #4801.
        # Bands are 1 MHz wide and centred on the MHz.

        def get_band_for_image(image):
            # Returns the band number corresponding to a particular image.
            return tkp.db.execute("""
                SELECT band
                FROM image
                WHERE image.id = %(id)s
            """, {"id": image.id}).fetchone()[0]

        data = copy(self.image_data)
        dataset1 = DataSet(data={'description': self._testMethodName},
                           database=self.database)

        # Example frequencies/bandwidths supplied in bug report.
        data['freq_eff'] = 124021911.62109375
        data['freq_bw'] = 1757812.5

        # image1 and image2 are exactly the same, so should be in the same
        # band.
        image1 = Image(dataset=dataset1, data=data)
        image2 = Image(dataset=dataset1, data=data)
        self.assertEqual(get_band_for_image(image1), get_band_for_image(image2))

        # Another image at a frequency 1 MHz different should be in
        # a different band...
        data['freq_eff'] = data['freq_eff'] - 1e6
        image3 = Image(dataset=dataset1, data=data)
        self.assertNotEqual(get_band_for_image(image1), get_band_for_image(image3))

        # ...even if it has a huge bandwidth.
        data['freq_bw'] *= 100
        image4 = Image(dataset=dataset1, data=data)
        self.assertNotEqual(get_band_for_image(image1), get_band_for_image(image4))

        # Finally, this image should be in the same band, since it's at an only
        # slightly different frequency.
        data['freq_eff'] = 123924255.37109375
        data['freq_bw'] = 1953125.0
        image5 = Image(dataset=dataset1, data=data)
        self.assertEqual(get_band_for_image(image1), get_band_for_image(image5))

    @requires_database()
    def test_frequency_range(self):
        """
        Determine range of frequencies supported by DB schema.
        """

        def get_freq_for_image(image):
            # Returns the stored frequency corresponding to a particular image.
            return tkp.db.execute("""
                SELECT freq_central
                FROM image
                    ,frequencyband
                WHERE image.id = %(id)s
                  AND image.band = frequencyband.id
            """, {"id": image.id}).fetchone()[0]

        dataset = DataSet(data={'description': self._testMethodName},
                   database=self.database)
        data = copy(self.image_data)

        data['freq_eff'] = 1e6  # 1MHz
        data['freq_bw'] = 1e3 # 1KHz
        mhz_freq_image = Image(dataset=dataset, data=data)
        self.assertEqual(data['freq_eff'], get_freq_for_image(mhz_freq_image))

        data['freq_eff'] = 100e9  # 100 GHz (e.g. CARMA)
        data['freq_bw'] = 5e9 # 5GHz
        ghz_freq_image = Image(dataset=dataset, data=data)
        self.assertEqual(data['freq_eff'], get_freq_for_image(ghz_freq_image))

        data['freq_eff'] = 5e15  # 5 PHz (e.g. UV obs)
        data['freq_bw'] = 1e14 # 5GHz
        phz_freq_image = Image(dataset=dataset, data=data)
        self.assertEqual(data['freq_eff'], get_freq_for_image(phz_freq_image))

if __name__ == "__main__":
    unittest.main()
