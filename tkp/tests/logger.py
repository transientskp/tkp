import unittest
import logging
import StringIO
import sys
import os
import tkp.config



# To do: find a smart/good way to capture the output.
# Perhaps in an external shell script that runs this
# test.

class TestLogger(unittest.TestCase):

    def setUp(self):
        #self.stderr = sys.stderr
        #self.out = StringIO.StringIO()
        #sys.stderr = self.out
        self.logger = logging.getLogger('tkp')
        self.buffer = StringIO.StringIO()
        self.assertIsInstance(self.logger.handlers[0], logging.StreamHandler)
        self.logger.handlers[0] = logging.StreamHandler(self.buffer)

    def tearDown(self):
        self.logger.handlers[0] = logging.StreamHandler()
        
    def test_basics(self):
        self.logger.critical('critical')
        self.assertEqual(self.buffer.getvalue(), 'critical\n')
        self.buffer.truncate(0)
        self.logger.error('error')
        self.assertEqual(self.buffer.getvalue(), 'error\n')
        self.buffer.truncate(0)
        self.logger.warning('warning')
        self.assertEqual(self.buffer.getvalue(), '')
        self.buffer.truncate(0)
        self.logger.info('info')
        self.assertEqual(self.buffer.getvalue(), '')
        self.buffer.truncate(0)
        self.logger.debug('debug')
        self.assertEqual(self.buffer.getvalue(), '')
        self.buffer.truncate(0)

    def test_levels(self):
        #self.assertIsInstance(self.logger.handlers[0], logging.StreamHandler)
        #self.logger.handlers[0] = logging.StreamHandler(self.buffer)
        self.logger.setLevel(logging.DEBUG)

        self.logger.critical('critical')
        self.assertEqual(self.buffer.getvalue(), 'critical\n')
        self.buffer.truncate(0)
        self.logger.error('error')
        self.assertEqual(self.buffer.getvalue(), 'error\n')
        self.buffer.truncate(0)
        self.logger.warning('warning')
        self.assertEqual(self.buffer.getvalue(), 'warning\n')
        self.buffer.truncate(0)
        self.logger.info('info')
        self.assertEqual(self.buffer.getvalue(), 'info\n')
        self.buffer.truncate(0)
        self.logger.debug('debug')
        self.assertEqual(self.buffer.getvalue(), 'debug\n')
        self.buffer.truncate(0)

    
if __name__ == "__main__":
    unittest.main()
