import unittest

import time
from tkp.db.orm import DataSet
from tkp.db.general import update_dataset_process_end_ts
from tkp.db import execute as db_query
from tkp.testutil.decorators import requires_database

@requires_database()
class TestProcessTime(unittest.TestCase):
    def test_set_process_timestamps(self):
        dataset = DataSet(data={'description': 'test dataset'})
        time.sleep(1)
        update_dataset_process_end_ts(dataset.id)
        start_time, end_time = db_query("""
            SELECT process_start_ts, process_end_ts
            FROM dataset
            WHERE id = %(id)s
        """, {"id": dataset.id}).fetchone()
        self.assertLess(start_time, end_time)
