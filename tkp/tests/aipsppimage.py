# Tests for generic utility functions written for the TKP pipeline.

import unittest
import os
import tkp.sourcefinder.accessors as accessors
import tkp.sourcefinder.image as image
import tkp.config


DATAPATH = tkp.config.config['test']['datapath']


class AIPSppImageTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(DATAPATH, 'CX3_peeled.image/')
        # Beam here is a random beam, in this case the WENSS beam without the declination dependence.
        self.my_aipsppim = accessors.AIPSppImage(self.filename,beam=(54./3600,54./3600,0.))
        self.my_im = image.ImageData(self.my_aipsppim)

    def testsextractPython(self):
        self.my_im.sextract(det=15)

if __name__ == '__main__':
    unittest.main()
