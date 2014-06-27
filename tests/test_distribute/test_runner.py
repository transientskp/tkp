import unittest
import tkp.distribute


class TestRunner(unittest.TestCase):
    def test_runner(self):
        for method in 'serial', 'celery', 'multiproc':
            tkp.distribute.Runner(method)

        for method in 'serial', 'multiproc':  # can't test celery without broker
            runner = tkp.distribute.Runner(method)
            runner.map("persistence_node_step", [])

    def test_set_cores(self):
        cores = 10
        for method in 'serial', 'celery':
            tkp.distribute.Runner(method, cores=cores)
        multiproc_runner = tkp.distribute.Runner('multiproc', cores=cores)
        print dir(multiproc_runner.module)
        assert(multiproc_runner.module.pool._processes == cores)


    def test_invalid_runner(self):
        self.assertRaises(NotImplementedError, tkp.distribute.Runner, 'invalid')

    def test_invalid_function(self):
        celery_runner = tkp.distribute.Runner('serial')
        self.assertRaises(NotImplementedError, celery_runner.map, "invalid",
                          range(5))