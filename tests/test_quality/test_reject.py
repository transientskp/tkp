import unittest
import tkp.quality
import tkp.db
import tkp.db.quality
import tkp.db.database
from sqlalchemy.exc import DatabaseError
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs


class TestReject(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.fake_images = db_subs.generate_timespaced_dbimages_data(n_images=1)
        self.dataset = tkp.db.DataSet(data={'description':
                                                  "Reject:" + self._testMethodName})
        self.image = tkp.db.Image(data=self.fake_images[0],
                                        dataset=self.dataset)

    def tearDown(self):
        tkp.db.rollback()

    def test_rejectrms(self):
        tkp.db.quality.unreject(self.image.id)
        tkp.db.quality.reject(self.image.id,
                                    tkp.db.quality.reason['rms'].id,
                                    "10 times too high")
        query = "select count(*) from rejection where image=%s"
        args = (self.image.id,)
        cursor = tkp.db.execute(query, args)
        self.assertEqual(cursor.fetchone()[0], 1)

    def test_unreject(self):
        tkp.db.quality.unreject(self.image.id)
        query = "select count(*) from rejection where image=%s"
        args = (self.image.id,)
        cursor = tkp.db.execute(query, args)
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_unknownreason(self):
        self.assertRaises(DatabaseError,
              tkp.db.quality.reject, self.image.id, 666666, "bad reason")

    def test_all_reasons_present_in_database(self):
        for reason in tkp.db.quality.reason.values():
            tkp.db.quality.reject(self.image.id, reason.id, "comment")
            tkp.db.quality.unreject(self.image.id)

    def test_isrejected(self):
        tkp.db.quality.unreject(self.image.id)
        self.assertFalse(tkp.db.quality.isrejected(self.image.id))
        tkp.db.quality.reject(self.image.id,
                                    tkp.db.quality.reason['rms'].id,
                                    "10 times too high")
        self.assertEqual(tkp.db.quality.isrejected(self.image.id),
                         [tkp.db.quality.reason['rms'].desc +
                          ': 10 times too high', ])

if __name__ == '__main__':
    unittest.main()
