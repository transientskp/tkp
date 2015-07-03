import os
import unittest


def requires_database():
    if os.environ.get("TKP_DISABLEDB", False):
        return unittest.skip("Database functionality disabled in configuration")
    return lambda func: func


def requires_mongodb():
    if os.environ.get("TKP_DISABLEMONGODB", False):
        return unittest.skip("mongodb functionality disabled in configuration")
    return lambda func: func


def requires_data(*args):
    for filename in args:
        if not os.path.exists(filename):
            return unittest.skip("Test data (%s) not available" % filename)
    return lambda func: func


def requires_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return unittest.skip("Required module (%s) not available" % module_name)
    return lambda func: func


def duration(test_duration):
    max_duration = float(os.environ.get("TKP_MAXTESTDURATION", False))
    if max_duration:
        if max_duration < test_duration:
            return unittest.skip(
             "Tests of duration > %s disabled with TKP_MAXTESTDURATION" %
                max_duration)
    return lambda func: func


def requires_test_db_managed():
    """
    This decorator is used to disable tests that do potentially low level
    database management operations like destroy and create. You can enable
    these tests by setting the TKP_TESTDBMANAGEMENT environment variable.
    """
    if os.environ.get('TKP_DBENGINE', 'postgresql') == 'monetdb':
        return unittest.skip("DB management tests not supported for Monetdb,"
                             "must be tested manually.")

    if os.environ.get("TKP_TESTDBMANAGEMENT", False):
        return lambda func: func
    return unittest.skip("DB management tests disabled, TKP_TESTDBMANAGEMENT"
                         " not set")

def high_ram_requirements():
    """
    Used to disable tests that break Travis due to out-of-memory issues.
    """
    if os.environ.get("TRAVIS", False):
        return unittest.skip("High-ram requirement unit-tests disabled on Travis")
    return lambda func: func