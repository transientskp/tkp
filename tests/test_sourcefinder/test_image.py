import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
from decorators import requires_data
from decorators import requires_module
import tkp.sourcefinder 
from tkp.sourcefinder import image as sfimage
import tkp.config
from tkp.utility import accessors
from tkp.utility.uncertain import Uncertain

import numpy as np
import os

DATAPATH = tkp.config.config['test']['datapath']

BOX_IN_BEAMPIX = 10 #HARDCODING - FIXME! (see also monitoringlist recipe)

#
class TestNumpySubroutines(unittest.TestCase):
    def testBoxSlicing(self):
        """testBoxSlicing
        
            Tests a routine to return a window on an image.
                
            Previous implementation returned correct sized box,
            but central pixel was often offset unnecessarily.
            This method always returns a centred chunk.
   
        """
        
        a = np.arange(1,101)
        a= a.reshape(10,10)
        x,y = 3,3
        central_value = a[y,x] #34
        
        round_down_to_single_pixel = a[sfimage.ImageData.box_slice_about_pixel(x, y, 0.9)]
        self.assertEquals(round_down_to_single_pixel, [[central_value]])
        
        chunk_3_by_3 = a[sfimage.ImageData.box_slice_about_pixel(x, y, 1)]
        self.assertEquals(chunk_3_by_3.shape, (3,3))
        self.assertEqual(central_value, chunk_3_by_3[1,1])        
        
        chunk_3_by_3_round_down = a[sfimage.ImageData.box_slice_about_pixel(x, y, 1.9)]
        self.assertListEqual( list(chunk_3_by_3.reshape(9)),
                              list(chunk_3_by_3_round_down.reshape(9))
                              )
    
        

class TestFitFixedPositions(unittest.TestCase):
    """Test various fitting cases where the pixel position is predetermined"""
    
    @requires_data(os.path.join(DATAPATH, 'NCP_sample_image_1.fits'))
    def setUp(self):
        """NB the required image has been committed to the tkp/data subversion repository.
        
            (See tkp/data/unittests/tkp_lib for a full copy of all the unittest data).
            
            Source positions / background positions were simply picked out by eye in DS9
        """
        self.image = accessors.sourcefinder_image_from_accessor(
                       accessors.FitsFile(os.path.join(DATAPATH, 'NCP_sample_image_1.fits'))
                       )
        
        
        
        self.assertListEqual(list(self.image.data.shape),[1024,1024])
        self.boxsize = BOX_IN_BEAMPIX*max(self.image.beam[0], self.image.beam[1])
        
        self.bright_src_posn = (215.83993,86.307504)  #RA, DEC
        self.background_posn = (186.33731,82.70002)    #RA, DEC
        
        ##NB These are simply plucked from a previous run,
        # so they merely ensure *consistent*, rather than *correct*, results.
        self.known_fit_results = [215.84 , 86.31 , 9.88] #RA, DEC, PEAK
        
        pass    
    
    def testSourceAtGivenPosition(self):
        posn = self.bright_src_posn
        img=self.image
        results = self.image.fit_fixed_positions(sources = [posn], 
                                       boxsize = self.boxsize,
                                       threshold=0.0)[0]
    
        self.assertAlmostEqual(results.ra.value, self.known_fit_results[0],
                               delta = 0.01)
        self.assertAlmostEqual(results.dec.value, self.known_fit_results[1],
                               delta = 0.01)
        self.assertAlmostEqual(results.peak.value, self.known_fit_results[2],
                               delta = 0.01)
    
#        print "BOXSIZE:", self.boxsize
#        print "XY:", img.wcs.s2p(posn)
#        print "Results:", results
#        print
#    
    def testLowFitThreshold(self):
        """testLowFitThreshold
        
        If we supply an extremely low threshold
        do we get a similar result to a zero threshold, for a bright source? 
        """
        
        posn = self.bright_src_posn
        img=self.image
        
#        with self.assertRaises(ValueError):
        low_thresh_results = self.image.fit_fixed_positions(sources = [posn], 
                                   boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]),
                                   threshold = -1e20)[0]
        self.assertAlmostEqual(low_thresh_results.ra.value, self.known_fit_results[0],
                               delta = 0.01)
        self.assertAlmostEqual(low_thresh_results.dec.value, self.known_fit_results[1],
                               delta = 0.01)
        self.assertAlmostEqual(low_thresh_results.peak.value, self.known_fit_results[2],
                               delta = 0.01)
        
        
#        print "Results:", low_thresh_results
#        print
        
    def testHighFitThreshold(self):
        """testHighFitThreshold
        
        If we supply an extremely high threshold, we expect to get back 
        a fitting error since all pixels should be masked out.
        """
    
        posn = self.bright_src_posn
        img=self.image
        with self.assertRaises(ValueError):
            results = self.image.fit_fixed_positions(sources = [posn], 
                                       boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]),
                                       threshold = 1e20)
#        print "XY:", img.wcs.s2p(posn)
#        print "Results:", results
#        print


#    
    def testBackgroundAtGivenPosition(self):
        """testBackgroundAtGivenPosition
        
        I.E. no source at given position (but still in the image frame)
        
        Note, if we request zero threshold, then the region will be unfittable,
        since it is largely below that thresh.
        
        Rather than pick an arbitrarily low threshold, we set it to None.
        
        """

        img=self.image
        results = self.image.fit_fixed_positions(
                                     sources = [self.background_posn], 
                                     boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]), 
                                     threshold = None
                                     )[0]
                                     
#        print "XY:", img.wcs.s2p(posn)
#        print "Results:", results
        self.assertAlmostEqual(results.peak.value, 0, 
                               delta = results.peak.error*1.0)
#        print
        

        
    def testGivenPositionOutsideImage(self):
        """testGivenPositionOutsideImage
        
        If given position is outside image then result should be NoneType"""
        img = self.image
        p1 = img.wcs.p2s((0,0))
        p2 = img.wcs.p2s((img.data.shape[0], img.data.shape[1]))
#        print "Sky lower left",p1 
#        print "Sky upper right", p2
        posn_out_of_img = (p1[0] - 10.0 / 3600.0 , (p1[1] + p2[1] / 2.0) )
        results = self.image.fit_fixed_positions(sources = [posn_out_of_img], 
                                       boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]))
#        print "XY:", img.wcs.s2p(posn_out_of_img)
#        print "Results:" , results
        self.assertListEqual([None], results)
        
        

    def testTooCloseToEdgePosition(self):
        """testTooCloseToEdgePosition
        
        Same if right on the edge -- too few pixels to fit"""
        img = self.image
        
        boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1])
        edge_posn = img.wcs.p2s((0 + boxsize/2 -2, img.data.shape[1]/2.0))
        
        results = self.image.fit_fixed_positions(
                                    sources = [edge_posn], 
                                    boxsize = boxsize,
                                    threshold = -1e10
                                    )
#        print "Posn:", edge_posn
#        print "XY:", img.wcs.s2p(edge_posn)
#        print "Results:" , results
        self.assertListEqual([None], results)
        
    def testErrorBoxOverlapsEdge(self):
        """testErrorBoxOverlapsEdge
        
        Sometimes when fitting at a fixed position,
        we get extremely large uncertainty values.
        
        These create an error box on position which extends outside the image,
        causing errors when we try to calculate the RA / Dec uncertainties.
        
        This test ensures we handle this case gracefully.
        """
        
        img = self.image
        
        fake_params = tkp.sourcefinder.extract.ParamSet()
        fake_params.values.update({
                           'peak': Uncertain(0.0,0.5),
                           'flux':Uncertain(0.0,0.5),
                           'xbar': Uncertain(5.5 , 10000.5), # Danger Will Robinson
                           'ybar': Uncertain(5.5 , 3),
                           'semimajor': Uncertain(4 , 200),
                           'semiminor': Uncertain(4 , 2),
                           'theta': Uncertain(30 , 10),
                           })
        fake_params.sig = 0
        det = tkp.sourcefinder.extract.Detection(fake_params, img)
        #Raises runtime error prior to bugfix for issue #3294
        det._physical_coordinates() 
        self.assertEqual(det.ra.error, float('inf'))
        self.assertEqual(det.dec.error, float('inf'))
        
        
    
        
class TestSimpleImageSourceFind(unittest.TestCase):
    """Now lets test drive the routines which find new sources"""
    
#    def setUp(self):
#        """NB the required image has been committed to the tkp/data subversion repository.
#            (See tkp/data/unittests/tkp_lib for a full copy of all the unittest data).
#        """
        
    @requires_data(os.path.join(DATAPATH, 'GRB120422A/GRB120422A-120429.fits'))
    def testSingleSourceExtraction(self):
        """testSingleSourceExtraction
        
        From visual inspection we only expect a single source in the image,
        at around 5 or 6 sigma detection level."""
        
        known_result = (136.89603241069054, 14.022184792492785, #RA, DEC 
                     0.0005341819139061954, 0.0013428186757078464, #Err, Err
                      0.0007226590529214518, 0.00010918184742211533, #Peak flux, err
                      0.0006067963179204716, 0.00017037685531724465, #Integrated flux, err
                      6.192259965962862, 25.516190123153514, #Significance level, Beam semimajor-axis width (arcsec)
                      10.718798843620489, 178.62899212789304) #Beam semiminor-axis width (arcsec), Beam parallactic angle
    
        
        self.image = accessors.sourcefinder_image_from_accessor(
                       accessors.FitsFile(os.path.join(DATAPATH, 'GRB120422A/GRB120422A-120429.fits'))
                       )
        
        results = self.image.extract(det=5, anl=3)
        results = [result.serialize() for result in results]
        self.assertTupleEqual(known_result, results[0])
        
