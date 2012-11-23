import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import sys

import monetdb

import tkp.quality
import tkp.database
import tkp.database.quality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_subs
from decorators import requires_database


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
        tkp.database.quality.unreject(self.database.connection, self.image.id)
        tkp.database.quality.reject(self.database.connection, self.image.id,
                                    tkp.database.quality.reason['rms'].id,
                                    "10 times too high")
        self.database.execute("select count(*) from rejection where image=%s" %
                              self.image.id)
        self.assertEqual(self.database.fetchone()[0], 1)

    def test_unreject(self):
        tkp.database.quality.unreject(self.database.connection, self.image.id)
        self.database.execute("select count(*) from rejection where image=%s" %
                              self.image.id)
        self.assertEqual(self.database.fetchone()[0], 0)

    def test_unknownreason(self):
        self.assertRaises(monetdb.exceptions.OperationalError,
                          tkp.database.quality.reject, self.database.connection,
                          self.image.id, 666666, "bad reason")

    def test_isrejected(self):
        tkp.database.quality.unreject(self.database.connection, self.image.id)
        self.assertFalse(tkp.database.quality.isrejected(self.database.connection,
                                                         self.image.id))
        tkp.database.quality.reject(self.database.connection, self.image.id,
                                    tkp.database.quality.reason['rms'].id,
                                    "10 times too high")
        self.assertEqual(tkp.database.quality.isrejected(self.database.connection,
                                                         self.image.id),
                         [tkp.database.quality.reason['rms'].desc +
                          ': 10 times too high', ])

if __name__ == '__main__':
    unittest.main()
