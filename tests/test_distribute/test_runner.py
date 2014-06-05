import unittest
import tkp.distribute
import logging

logging.basicConfig(level=logging.DEBUG)


class TestRunner(unittest.TestCase):
    def test_runner(self):
        celery_runner = tkp.distribute.Runner('celery')
        celery_runner.run("bogus")
        celery_runner.bogus()
        multiproc_runner = tkp.distribute.Runner('multiproc')
        multiproc_runner.run("bogus")
        multiproc_runner.bogus()

    def test_invalid_runner(self):
        self.assertRaises(NotImplementedError, tkp.distribute.Runner, 'invalid')

    def test_invalid_function(self):
        celery_runner = tkp.distribute.Runner('celery')
        celery_runner.run("invalid")