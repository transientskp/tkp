# Tests for generic utility functions written for the TKP pipeline.

import unittest
import os
from tkp.utility import accessors
import tkp.sourcefinder.image as image
import tkp.config


DATAPATH = tkp.config.config['test']['datapath']


class AIPSppImage(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(DATAPATH, 'CX3_peeled.image/')
        # Beam here is a random beam, in this case the WENSS beam without the declination dependence.
        aipsppim = accessors.AIPSppImage(self.filename, beam=(54./3600, 54./3600, 0.))
        self.my_im = image.ImageData(aipsppim.data, aipsppim.beam, aipsppim.wcs)

    def testsextractPython(self):
        self.my_im.sextract(det=15)

if __name__ == '__main__':
    unittest.main()
