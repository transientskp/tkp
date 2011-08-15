# Tests for generic utility functions written for the TKP pipeline.

import unittest
import os
from tkp.utility import accessors
from tkp.sourcefinder import image
import tkp.config
# This test should not be run unless pyrap is available.
import pyrap


DATAPATH = tkp.config.config['test']['datapath']


class AIPSppImage(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(DATAPATH, 'CX3_peeled.image/')
        # Beam here is a random beam, in this case the WENSS beam
        # without the declination dependence.
        aipsppim = accessors.AIPSppImage(self.filename,
                                         beam=(54./3600, 54./3600, 0.))
        self.image = image.ImageData(aipsppim.data, aipsppim.beam,
                                     aipsppim.wcs)

    def testExtractPython(self):
        self.image.extract(det=15)

if __name__ == '__main__':
    unittest.main()
