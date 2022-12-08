
import unittest
import tkp.quality
import tkp.db
from tkp.db.model import Rejection, Rejectreason
import tkp.db.quality as dbqual
import tkp.db.database
from sqlalchemy.exc import DatabaseError, IntegrityError
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs


@requires_database()
class TestReject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = tkp.db.Database()

    def setUp(self):
        self.session = self.db.Session()
        self.fake_images = db_subs.generate_timespaced_dbimages_data(n_images=1)
        self.dataset = tkp.db.DataSet(data={'description':
                                                "Reject:" + self._testMethodName})
        self.image = tkp.db.Image(data=self.fake_images[0],
                                  dataset=self.dataset)

    def tearDown(self):
        self.session.rollback()
        tkp.db.rollback()
        pass

    def test_rejectrms_and_unreject(self):
        dbqual.reject(self.image.id,
                      dbqual.reject_reasons['rms'],
                      "10 times too high",
                      self.session)
        image_rejections_q = self.session.query(Rejection).filter(
            Rejection.image_id == self.image.id)
        self.assertEqual(image_rejections_q.count(), 1)
        dbqual.unreject(self.image.id, self.session)
        self.assertEqual(image_rejections_q.count(), 0)

    def test_unknownreason(self):
        with self.assertRaises(IntegrityError):
            dbqual.reject(self.image.id,
                          Rejectreason(id=666666, description="foobar"),
                          comment="bad reason",
                          session=self.session)
            self.session.flush()

    def test_all_reasons_present_in_database(self):
        for reason in list(dbqual.reject_reasons.values()):
            dbqual.reject(self.image.id, reason, "comment", self.session)
            dbqual.unreject(self.image.id, self.session)

    def test_isrejected(self):
        dbqual.unreject(self.image.id, self.session)
        self.assertFalse(dbqual.isrejected(self.image.id, self.session))

        rms_reason = dbqual.reject_reasons['rms']
        comment = "10 times too high"

        reason_comment_str = "{}: {}".format(rms_reason.description, comment)
        dbqual.reject(self.image.id,
                      rms_reason,
                      comment,
                      self.session)
        self.assertEqual(dbqual.isrejected(self.image.id, self.session),
                         [ reason_comment_str ])

    def test_rejectreasons_sync(self):
        """
        Delete a rejectreason, then re-sync and double check the counts match.
        """
        reason = self.session.query(Rejectreason).all()[-1]
        print("Deleting reason id", reason.id)
        self.session.delete(reason)
        self.assertNotEqual(
            self.session.query(Rejectreason).count(),
            len(dbqual.reject_reasons))

        dbqual.sync_rejectreasons(self.session)
        self.session.flush()
        self.assertEqual(
            self.session.query(Rejectreason).count(),
            len(dbqual.reject_reasons))



if __name__ == '__main__':
    unittest.main()
