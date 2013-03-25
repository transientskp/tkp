import numpy

import unittest2 as unittest

from tkp.utility import sigmaclip


class TestSigma(unittest.TestCase):
    """Verify calculation of standard deviation"""
    
    def setUp(self):
        self.data = numpy.array([22., 24., 23., 31., 22., 21., 22.])
        self.errors = numpy.array([2., 2., 2., 10., 1.5, 2.5, 1.5])
        self.data2d = numpy.arange(6).reshape((3,2))
        self.errors2d = numpy.array([0.25, 0.75]*3).reshape(self.data2d.shape)
        self.data3d = numpy.arange(24).reshape((2,3,4))
        self.errors3d = numpy.array([0.25, 0.75]*12).reshape(self.data3d.shape)
        
    def test_unweighted(self):
        """Calculate unweighted mean and sample standard deviation"""

        self.mean, self.sigma = sigmaclip.calcsigma(data=self.data, errors=None, mean=None)
        self.assertAlmostEqual(self.mean, 23.5714285714)
        self.assertAlmostEqual(self.sigma, 3.40867241299)

    def test_weighted(self):
        """Calculate weighted mean and sample standard deviation"""

        self.mean, self.sigma = sigmaclip.calcsigma(data=self.data, errors=self.errors, mean=None)
        self.assertAlmostEqual(self.mean, 22.3759213759)
        self.assertAlmostEqual(self.sigma, 1.15495684937)

    def test_axis(self):
        """Test sigma calculation when axis is not None"""


        self.mean, self.sigma =  sigmaclip.calcsigma(self.data2d, self.errors2d, errors_as_weight=True)
        self.assertAlmostEqual(self.mean, 2.75)
        self.assertAlmostEqual(self.sigma, 1.898753053)

        self.mean, self.sigma =  sigmaclip.calcsigma(self.data2d, self.errors2d, axis=0, errors_as_weight=True)
        self.assertEqual((abs(self.mean - numpy.array([2.0, 3.0])) < 1e-7).all(), True)
        self.assertEqual((abs(self.sigma - numpy.array([2.0, 2.0])) < 1e-7).all(), True)

        self.mean, self.sigma =  sigmaclip.calcsigma(self.data2d, self.errors2d, axis=1, errors_as_weight=True)
        self.assertEqual((abs(self.mean - numpy.array([0.75, 2.75, 4.75])) < 1e-7).all(), True)
        self.assertEqual((abs(self.sigma - numpy.array(
            [0.70710678, 0.70710678, 0.70710678])) < 1e-7).all(), True)

        self.mean, self.sigma =  sigmaclip.calcsigma(self.data3d, self.errors3d, axis=None, errors_as_weight=True)
        self.assertAlmostEqual(self.mean, 11.75)
        self.assertAlmostEqual(self.sigma, 7.10517533095)

        self.mean, self.sigma =  sigmaclip.calcsigma(self.data3d, self.errors3d, axis=0, errors_as_weight=True)
        mean = numpy.array([[6., 7., 8., 9.], [10., 11., 12., 13.], [14., 15., 16., 17.]])
        sigma = numpy.array([[8.48528137, 8.48528137, 8.48528137, 8.48528137], 
                             [8.48528137, 8.48528137, 8.48528137, 8.48528137],
                             [8.48528137, 8.48528137, 8.48528137, 8.48528137]])
        self.assertEqual((abs(self.mean - mean) < 1e-7).all(), True)
        self.assertEqual((abs(self.sigma - sigma) < 1e-7).all(), True)

        self.mean, self.sigma =  sigmaclip.calcsigma(self.data3d, self.errors3d, axis=1, errors_as_weight=True)
        mean = numpy.array([[4., 5., 6., 7.], [16., 17., 18., 19.]])
        sigma = numpy.array([[4., 4., 4., 4.], [4., 4., 4., 4.]])
        self.assertEqual((abs(self.mean - mean) < 1e-7).all(), True)
        self.assertEqual((abs(self.sigma - sigma) < 1e-7).all(), True)

        self.mean, self.sigma =  sigmaclip.calcsigma(self.data3d, self.errors3d, axis=2, errors_as_weight=True)
        mean = numpy.array([[1.75, 5.75, 9.75], [13.75, 17.75, 21.75]])
        sigma = numpy.array([[1.31425748, 1.31425748, 1.31425748], [1.31425748, 1.31425748, 1.31425748]])
        self.assertEqual((abs(self.mean - mean) < 1e-7).all(), True)
        self.assertEqual((abs(self.sigma - sigma) < 1e-7).all(), True)
        

class TestClip(unittest.TestCase):
    """Verify sigma-clip algorithm"""

    def setUp(self):
        self.data = numpy.array([22., 24., 23., 31., 22., 21., 22.])
        self.errors = numpy.array([2., 2., 2., 10., 1.5, 2.5, 1.5])
        self.data3d = numpy.arange(24).reshape((2,3,4))
        self.errors3d = numpy.array([0.25, 0.75]*12).reshape(self.data3d.shape)

    def test_unweighted(self):
        """Perform unweighted sigma clipping"""

        INDICES = numpy.ones(len(self.data), dtype=numpy.bool)
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=None, niter=0,
                            siglow=1., sighigh=1., use_median=False)
        self.assertEqual((indices == INDICES).all(), True)

        INDICES[3] = False
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=None, niter=1,
                            siglow=1., sighigh=1., use_median=False)
        self.assertEqual((indices == INDICES).all(), True)

        INDICES[1] = INDICES[5] = False
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=None, niter=2,
                            siglow=1., sighigh=1., use_median=False)
        self.assertEqual((indices == INDICES).all(), True)

    def test_weighted(self):
        """Perform weighted sigma clipping"""

        INDICES = numpy.ones(len(self.data), dtype=numpy.bool)
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors, niter=0,
                            siglow=1., sighigh=1., use_median=False)
        self.assertEqual((indices == INDICES).all(), True)

        INDICES[1] = INDICES[3] = INDICES[5] = False
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors, niter=1,
                            siglow=1., sighigh=1., use_median=False)
        self.assertEqual((indices == INDICES).all(), True)

        INDICES[2] = False
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors, niter=2,
                            siglow=1., sighigh=1., use_median=False)
        self.assertEqual((indices == INDICES).all(), True)

        # With three dimensional data
        indices, niter = sigmaclip.sigmaclip(data=self.data3d, errors=self.errors3d, niter=2,
                            siglow=1., sighigh=1., use_median=True)
        INDICES = numpy.array([[[False, False, False, False],
                                [False, False, False, False],
                                [ True,  True,  True,  True]],
                               [[ True,  True,  True,  True],
                                [False, False, False, False],
                                [False, False, False, False]]], dtype=bool)
        self.assertEqual((indices == INDICES).all(), True)

    def test_clip2background(self):
        """Clip until no more data are clipped"""

        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors,
                                   niter=-100, siglow=3., sighigh=3.)
        self.assertEqual(niter, 2)

        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors,
                                   niter=-100, siglow=2., sighigh=2.)
        self.assertEqual(niter, 2)

        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors,
                                   niter=-100, siglow=1., sighigh=1.)
        self.assertEqual(niter, 3)

        INDICES = numpy.zeros(len(self.data), dtype=numpy.bool)
        indices, niter = sigmaclip.sigmaclip(data=self.data, errors=self.errors,
                                   niter=-100, siglow=.2, sighigh=.2)
        self.assertEqual((indices == INDICES).all(), True)
        self.assertEqual(niter, 1)

#    # This test is only to demonstrate that 
#    def test_temp(self):
#        data = numpy.ones(40) * 1e-6
#        errors = numpy.array(
#            [5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9, 8e-9, -8e-9,
#             2e-8, -2e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
#             2.5e-8, -2.5e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
#             1.5e-8, -1.5e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
#             1.5e-8, -1.5e-8, 5e-9, -5e-9, 1e-8, -1e-8, 5e-9, -5e-9,
#             ])
#        data[5] *= 2.
#        data[6] *= 4.
#        data[7] *= 2.
#        data[15] *= 4.
#        data[16] *= 8.
#        data[17] *= 8.
#        data[18] *= 4.
#        indices, niter = sigmaclip.sigmaclip(
#            data=data, errors=errors, niter=-50, siglow=3., sighigh=3.,
#            use_median=True)
#        print indices, niter
            
        
        
#     def test_median(self):
#         """Perform weighted clipping, using the median instead of the mean
# 
#         This test serves more as an example when use_median=True is useful,
#         instead of being an actual test
# 
#         """
# 
#         data = numpy.array([  1.00050253e-07, 9.94556560e-08, 9.98087079e-08, 1.00385932e-07,
#                               1.00588676e-07, 9.93362336e-08, 1.01789316e-07, 9.78764861e-08,
#                               1.00247563e-07, 1.06498718e-07, 1.25108083e-07, 1.68517930e-07,
#                               2.66448891e-07, 4.41022617e-07, 6.81483052e-07, 9.28143675e-07,
#                               1.08180783e-06, 1.07332256e-06, 9.06873741e-07, 6.55038891e-07,
#                               4.19654114e-07, 2.53581021e-07, 1.60712555e-07, 1.20588400e-07,
#                               1.06128891e-07, 1.02742995e-07, 1.00197065e-07, 9.95647473e-08,
#                               9.99406901e-08, 1.00907591e-07])
#         errors = numpy.array([5.02530407e-11, 5.44344425e-10, 1.91298435e-10, 3.85853234e-10,
#                               5.87858675e-10, 6.70865208e-10, 1.73788713e-09, 2.43447004e-09,
#                               1.32154904e-09, 1.09331204e-10, 1.88299671e-09, 3.93000464e-10,
#                               3.21700598e-10, 3.02688912e-10, 5.31036144e-10, 1.44421729e-09,
#                               1.53460347e-11, 2.24922675e-10, 1.94433102e-09, 6.39917259e-10,
#                               4.96645627e-10, 3.58418264e-10, 1.06204238e-09, 1.00367115e-10,
#                               3.46280240e-10, 1.39410035e-09, 6.55358587e-11, 4.77918509e-10,
#                               6.50952562e-11, 9.06936329e-10])
#         indices = sigmaclip.sigmaclip(data, errors=None, niter=3, siglow=2., sighigh=2.)
#         print sigmaclip.calcsigma(data, errors)
#         avg, std = calcmean(data[indices], errors[indices])
#         print indices
#         print numpy.median(data), avg, std
#         self.assertEqual(1, 1)
#         

    
if __name__ == "__main__":
    unittest.main()
