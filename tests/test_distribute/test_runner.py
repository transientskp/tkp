import unittest
import tkp.distribute


class TestRunner(unittest.TestCase):
    def test_runner(self):
        serial_runner = tkp.distribute.Runner('serial')
        serial_runner.map("bogus", range(5))
        multiproc_runner = tkp.distribute.Runner('multiproc')
        multiproc_runner.map("bogus", range(5))

    def test_invalid_runner(self):
        self.assertRaises(NotImplementedError, tkp.distribute.Runner, 'invalid')

    def test_invalid_function(self):
        celery_runner = tkp.distribute.Runner('serial')
        self.assertRaises(NotImplementedError, celery_runner.map, "invalid",
                          range(5))