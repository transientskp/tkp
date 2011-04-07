# Tests for generic utility functions written for the TKP pipeline.

import unittest
import tkp_lib.measurementset as ms
import tempfile, shutil

class MeasurementSetTestCase(unittest.TestCase):
    """A basic test case to ensure that reading MeasurementSets works. Could
    be extended to cover imaging etc(?).

    You'll need to source an aipsrc.
    
    This is hardcoded to use a LOFAR 15 12 hour dataset simulated by Casey
    Law. A more general system would be preferable, but I don't want to put
    the MS in Subversion!"""

    def setUp(self):
        self.path='/home/jds/simulated_data/L15_12h_const/'
        self.masterfile='L15_12h_const.MS'
        self.my_ms = ms.measurementset(self.path, self.masterfile)

    def testTime(self):
        self.assertEqual(self.my_ms.start_time(), 4691657894.9090004)
        self.assertEqual(self.my_ms.end_time(),   4691701084.9090004)
        self.assertEqual(self.my_ms.end_time() - self.my_ms.start_time(), self.my_ms.length())

    def testSelectAndImage(self):
        # This seems fairly comprehensively broken for now.
        tempfile.tempdir=''
        fname = tempfile.mktemp()
        try:
            minidata = self.my_ms.select_data(self.my_ms.start_time(), self.my_ms.start_time() + 60, fname, verbose=False)
            minidata.make_image(verbose=False)
        except:
            try: 
                shutil.rmtree(self.path + fname)
                shutil.rmtree(self.path + fname + '.img')
            except:
                pass
            self.fail()
        shutil.rmtree(self.path + fname)
        shutil.rmtree(self.path + fname + '.img')


if __name__ == '__main__':
    unittest.main()
