import unittest
from tkp.db.database import Database
from tkp.testutil.alchemy import gen_dataset, gen_image, gen_band,\
    gen_skyregion, gen_runningcatalog, gen_extractedsource
from tkp.testutil.decorators import requires_database
from tkp.db.model import Image

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TestDeleteDataset(unittest.TestCase):
    @requires_database()
    def test_delete_dataset(self):
        db = Database()
        dataset = gen_dataset('delete test')
        band = gen_band(dataset)
        skyregion = gen_skyregion(dataset)
        image = gen_image(band, dataset, skyregion)
        extractedsource = gen_extractedsource(image)
        runningcatalog = gen_runningcatalog(extractedsource, dataset)
        db.session.add_all((
            dataset, band, skyregion, image, extractedsource, runningcatalog,
        ))
        db.session.flush()

        db.session.delete(dataset)
        db.session.flush()

        images = db.session.query(Image).filter(Image.dataset==dataset).all()
        self.assertEqual(len(images), 0)

# this depends on store_in_db PR
"""
class TestDeleteImageData(unittest.TestCase):
    def test_delete_dataset(self):
        db = Database()
        dataset = gen_dataset('delete test')
        band = gen_band(dataset)
        skyregion = gen_skyregion(dataset)
        image = gen_image(band, dataset, skyregion)
        image.fits_data = 'bigdata'
        db.session.add_all((dataset, band, skyregion, image))
        db.session.flush()

        db.session.query(Image).\
            filter(Image.dataset==dataset).\
            update({Image.fits_data: None})
        db.session.flush()

        for i in db.session.query(Image).filter(Image.dataset==dataset).all():
            self.assertEqual(i.fits_data, None)
"""
