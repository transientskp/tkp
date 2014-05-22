import unittest
from tkp.db.configstore import store_config, fetch_config
from tkp.db import rollback, execute, Database
from tkp.db.general import insert_dataset


config = {'section1': {'key1': 'value1', 'key2': 2},
          'section2': {'key3': 'value3', 'key4': 4},
          'section3': {'key5': 0.20192, 'key4': 0.000001}}


class TestConfigStore(unittest.TestCase):
    def setUp(self):
        description = "TestConfigStore"
        self.dataset_id = insert_dataset(description)

    def tearDown(self):
        rollback()

    def test_config_store(self):
        store_config(config, self.dataset_id)
        query1 = """
        select count(id)
        from config
        where section=%s and key=%s and value=%s and dataset=%s
        """
        args1 = ('section1', 'key1', 'value1', self.dataset_id)
        num1 = execute(query1, args1).rowcount
        self.assertEquals(num1, 1)
        args2 = ('section2', 'key3', 'value3', self.dataset_id)
        num2 = execute(query1, args2).rowcount
        self.assertEquals(num2, 1)

    def test_bad_type(self):
        """
        We don't allow storing types not in tkp.db.confstore.types
        """
        bad_config = {'section4': {'key_badtype': ['bad, type']}}
        self.assertRaises(TypeError, store_config, bad_config, self.dataset_id)

    def test_bad_type_in_db(self):
        """
        fetch_config should raise TypeError if invalid type in DB
        """
        q = """
        INSERT INTO config (dataset, section, key, value, type)
        VALUES (%s, 'bad', 'type', '[]', 'list');
        """
        execute(q, (self.dataset_id,))
        self.assertRaises(TypeError, fetch_config, self.dataset_id)

    def test_config_fetch(self):
        store_config(config, self.dataset_id)
        fetched_config = fetch_config(self.dataset_id)
        self.assertEquals(config, fetched_config)

    def test_double_store(self):
        """
        storing the same data twice should fail
        """
        store_config(config, self.dataset_id)
        database = Database()
        if database.engine == "monetdb":
            # monetdb raises an OperationalError here, postgres (and probably others IntegrityError)
            exception = database.connection.OperationalError
        else:
            exception = database.connection.IntegrityError
        self.assertRaises(exception, store_config, config, self.dataset_id)
