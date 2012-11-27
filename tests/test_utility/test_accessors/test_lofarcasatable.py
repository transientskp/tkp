import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import os
from tkp.utility import accessors
from tkp.utility.accessors.lofarcasaimage import LofarCasaImage
import tkp.config
from tkp.testutil.decorators import requires_data


DATAPATH = tkp.config.config['test']['datapath']

casatable =  os.path.join(DATAPATH, 'casatable/L55596_000TO009_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

@requires_data(casatable)
class TestLofarCasaImage(unittest.TestCase):
    def test_casaimage(self):
        accessor = LofarCasaImage(casatable)
        sfimage = accessors.sourcefinder_image_from_accessor(accessor)