import numpy as np
import os

import unittest

from tkp.testutil.decorators import requires_data
import tkp.sourcefinder
from tkp.sourcefinder import image as sfimage
from tkp import accessors
from tkp.utility.uncertain import Uncertain
from tkp.testutil.data import DATAPATH

#
class TestParallelSourceFind():
    """Now lets test drive the sourc finder when different number of 
       processes are used""" 

    @requires_data(os.path.join(DATAPATH, 'GRB130828A/SWIFT_554620-130504.image'))
    def testDifferentProcesses(self):
        """ 
        Check that extracting a source from FITS gives the same result when
        different numbers of processes are used. Based on testWcsConversionConsistency
        in test_image.py
        """ 

        # Should run this on several files, including bad ones

        nproc_to_test = 8

        fits_image = accessors.sourcefinder_image_from_accessor(
                       accessors.FitsImage(os.path.join(DATAPATH,
                                        'GRB130828A/SWIFT_554620-130504.image')))

        ew_sys_err, ns_sys_err = 0.0, 0.0
        fits_results = fits_image.extract(det=5, anl=3)
        fits_results = [result.serialize(ew_sys_err, ns_sys_err) for result in fits_results]
        for np in range(1,nproc_to_test+1): 
            fits_image_np = accessors.sourcefinder_image_from_accessor(
                       accessors.FitsImage(os.path.join(DATAPATH,
                                        'GRB130828A/SWIFT_554620-130504.image')),nproc=np)
            fits_results_np = fits_image_np.extract(det=5, anl=3)
            fits_results_np = [result.serialize(ew_sys_err, ns_sys_err) for result in fits_results_np]
        
            self.assertEqual(fits_results,fits_result_np)
