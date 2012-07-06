import os
import tkp.config

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest

def requires_database():
    if tkp.config.config['database']['enabled']:
        tkp.config.config['database']['name']=tkp.config.config['test']['test_database_name']
        tkp.config.config['database']['user']=tkp.config.config['test']['test_database_name']
        tkp.config.config['database']['password']=tkp.config.config['test']['test_database_name']
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
