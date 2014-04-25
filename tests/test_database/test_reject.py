import unittest
import tkp.db
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database
import tkp.db.quality as db_quality
from tkp.db.associations import associate_extracted_sources

class TestRejection(unittest.TestCase):
    @requires_database()
    def test_rejected_initial_image(self):
        """
        An image which is rejected should not be taken into account when
        deciding whether a patch of sky has been previously observed, and
        hence whether any detections in that area are (potential) transients.

        Here, we create a database with two images. The first
        (choronologically) is rejected; the second contains a source. That
        source should not be marked as a transient.
        """

        dataset = tkp.db.DataSet(
            data={'description':"Trans:" + self._testMethodName},
            database=tkp.db.Database()
        )

        # We use a dataset with two images
        # NB the routine in db_subs automatically increments time between
        # images.
        n_images = 2
        db_imgs = [
            tkp.db.Image(data=im_params, dataset=dataset) for
            im_params in db_subs.example_dbimage_datasets(n_images)
        ]

       # The first image is rejected for an arbitrary reason
       # (for the sake of argument, we use an unacceptable RMS).
        tkp.db.quality.reject(
            db_imgs[0].id, tkp.db.quality.reason['rms'].id, self._testMethodName
        )

        # Since we rejected the first image, we only find a source in the
        # second.
        source = db_subs.example_extractedsource_tuple()
        db_imgs[1].insert_extracted_sources([source])

        # Standard source association procedure etc.
        associate_extracted_sources(db_imgs[1].id, 3.7)

        # Our source should _not_ be a transient. That is, there should be no
        # entries in the transient table for this dataset.
        cursor = tkp.db.execute("""\
            SELECT t.id FROM transient t, runningcatalog rc
                    WHERE t.runcat = rc.id
                      AND rc.dataset = %(ds_id)s
            """, {"ds_id": dataset.id}
        )
        self.assertEqual(cursor.rowcount, 0)
