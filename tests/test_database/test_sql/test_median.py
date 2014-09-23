import unittest
from tkp.db import execute, rollback


class testMedian(unittest.TestCase):
    def setUp(self):
        try:
            execute('drop table median_test')
        except:
            rollback()

        execute('create table median_test (i int, f float)')
        execute('insert into median_test values (1, 1.1)')
        execute('insert into median_test values (2, 2.1)')
        execute('insert into median_test values (3, 3.1)')

    def tearDown(self):
        rollback()

    def test_median(self):
        cursor = execute('select median(i), median(f) from median_test')
        median_i, median_f = cursor.fetchall()[0]
        self.assertEqual(median_i, 2)
        self.assertEqual(median_f, 2.1)
