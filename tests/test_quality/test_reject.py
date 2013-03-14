import unittest2 as unittest
import monetdb
import tkp.quality
import tkp.database
import tkp.database.quality
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs


class TestReject(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkp.database.DataBase()
        self.fake_images = db_subs.example_dbimage_datasets(n_images=1)
        self.dataset = tkp.database.DataSet(data={'description':
                                                  "Reject:" + self._testMethodName},
                                            database=self.database)
        self.image = tkp.database.Image(data=self.fake_images[0],
                                        dataset=self.dataset)

    def test_rejectrms(self):
        tkp.database.quality.unreject(self.image.id)
        tkp.database.quality.reject(self.image.id,
                                    tkp.database.quality.reason['rms'].id,
                                    "10 times too high")
        query = "select count(*) from rejection where image=%s"
        args = (self.image.id,)
        cursor = tkp.database.query(query, args)
        self.assertEqual(cursor.fetchone()[0], 1)

    def test_unreject(self):
        tkp.database.quality.unreject(self.image.id)
        query = "select count(*) from rejection where image=%s"
        args = (self.image.id,)
        cursor = tkp.database.query(query, args)
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_unknownreason(self):
        self.assertRaises(monetdb.exceptions.OperationalError,
              tkp.database.quality.reject, self.image.id, 666666, "bad reason")

    def test_isrejected(self):
        tkp.database.quality.unreject(self.image.id)
        self.assertFalse(tkp.database.quality.isrejected(self.image.id))
        tkp.database.quality.reject(self.image.id,
                                    tkp.database.quality.reason['rms'].id,
                                    "10 times too high")
        self.assertEqual(tkp.database.quality.isrejected(self.image.id),
                         [tkp.database.quality.reason['rms'].desc +
                          ': 10 times too high', ])

if __name__ == '__main__':
    unittest.main()
