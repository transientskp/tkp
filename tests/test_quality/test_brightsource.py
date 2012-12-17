import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
import tkp.quality.brightsource
import tkp.utility.accessors
import tkp.config

DATAPATH = tkp.config.config['test']['datapath']
testimage = os.path.join(DATAPATH,
    'casatable/L55614_020TO029_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

class TestBrightsource(unittest.TestCase):
    def test_check(self):
        image = tkp.utility.accessors.open(testimage)
        tkp.quality.brightsource.check(image)