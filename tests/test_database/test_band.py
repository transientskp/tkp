import unittest2 as unittest

import datetime
from tkp.testutil.decorators import requires_database
import tkp.db
from tkp.db.orm import DataSet, Image
from tkp.db.database import Database


class TestBand(unittest.TestCase):

    def setUp(self):
        import tkp.db.database
        self.database = tkp.db.database.Database()

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

        # Basic template data for each image.
        data = {
            'taustart_ts': datetime.datetime(1999, 9, 9),
            'url': '/path/to/image',
            'tau_time': 0,
            'beam_smaj_pix': float('inf'),
            'beam_smin_pix': float('inf'),
            'beam_pa_rad': float('inf'),
            'deltax': float(-0.01111),
            'deltay': float(0.01111),
            'centre_ra': 0,
            'centre_decl': 0,
            'xtr_radius' : 3
            }
        dataset1 = DataSet(data={'description': 'dataset with images'},
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


if __name__ == "__main__":
    unittest.main()
