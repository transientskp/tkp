import os
import tkp.config
import database_subroutines as testdb_subs

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest

def requires_database():
    if tkp.config.config['database']['enabled']:
        testdb_subs.use_test_database_by_default()
        return lambda func: func
    return unittest.skip("Database functionality disabled in configuration")

def requires_data(filename):
    if os.path.exists(filename):
        return lambda func: func
    return unittest.skip("Test data (%s) not available" % filename)

def requires_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return unittest.skip("Required module (%s) not available" % module_name)
    return lambda func: func
