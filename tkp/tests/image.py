import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest

from utility.decorators import requires_data
from utility.decorators import requires_database
from utility.decorators import requires_module
from tkp.sourcefinder import image
import os
import tkp.config
import wcslib
from tkp.utility import accessors



DATAPATH = tkp.config.config['test']['datapath']

BOX_IN_BEAMPIX = 10 #HARDCODING - FIXME! (see also monitoringlist recipe)

class TestFitFixedPositions(unittest.TestCase):
    """NB source positions / background positions were simply picked out by eye in DS9"""
    
    @requires_data(os.path.join(DATAPATH, 'NCP_sample_image_1.fits'))
    def setUp(self):
        """NB the required image has been committed to the tkp/data subversion repository.
        
            (See tkp/data/unittests/tkp_lib for a full copy of all the unittest data).
        """
        self.image = accessors.sourcefinder_image_from_accessor(
                       accessors.FitsFile(os.path.join(DATAPATH, 'NCP_sample_image_1.fits'))
                       )
        
        self.assertListEqual(list(self.image.data.shape),[1024,1024])
        self.boxsize = BOX_IN_BEAMPIX*max(self.image.beam[0], self.image.beam[1])
        pass    
        
    
    def testSourceAtGivenPosition(self):
        posn = (215.83993,86.307504)
        img=self.image
        results = self.image.fit_fixed_positions(sources = [posn], 
                                       boxsize = self.boxsize)
    
        print "BOXSIZE:", self.boxsize
        print "XY:", img.wcs.s2p(posn)
        print "Results:", results
        print
    
    def testBackgroundAtGivenPosition(self):
        """testBackgroundAtGivenPosition
        
        I.E. no source at given position (but still in the image frame)
        """
        posn = (186.33731,82.70002)
        img=self.image
        results = self.image.fit_fixed_positions(sources = [posn], 
                                       boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]))
        print "XY:", img.wcs.s2p(posn)
        print "Results:", results
        print
        
    def testFitThresholding(self):
        """testFitThresholding
        
        If we supply an extremely high threshold, we expect to get back 
        a fitting error since all pixels should be masked out.
        """
        pass
        posn = (186.33731,82.70002)
        img=self.image
        with self.assertRaises(ValueError):
            results = self.image.fit_fixed_positions(sources = [posn], 
                                       boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]),
                                       threshold = 1e20)
#        print "XY:", img.wcs.s2p(posn)
#        print "Results:", results
#        print
#    
        
    def testGivenPositionOutsideImage(self):
        """testGivenPositionOutsideImage
        
        Central position is checked, if outside image then result is NoneType"""
        img = self.image
        print 
        p1 = img.wcs.p2s((0,0))
        p2 = img.wcs.p2s((img.data.shape[0], img.data.shape[1]))
#        print "Sky lower left",p1 
#        print "Sky upper right", p2
        posn_out_of_img = (p1[0] - 10.0 / 3600.0 , (p1[1] + p2[1] / 2.0) )
        results = self.image.fit_fixed_positions(sources = [posn_out_of_img], 
                                       boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]))
        print "XY:", img.wcs.s2p(posn_out_of_img)
        print "Results:" , results
        self.assertListEqual([None], results)
        pass
        
    
#    def testEdgePosition(self):
#        img = self.image
#        print 
#        edge_posn = img.wcs.p2s((0, img.data.shape[1]/2.0))
#
#        results = self.image.fit_fixed_positions(sources = [edge_posn], 
#                                       boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1]))
#        print "XY:", img.wcs.s2p(edge_posn)
#        print "Results:" , results
#        
#        pass
    
#    def testHalfABoxFromEdgePosition(self):
        """Passes same as a regular position"""
#        img = self.image
#        print 
#        
#        boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1])
#        edge_posn = img.wcs.p2s((0 + boxsize/2 -1, img.data.shape[1]/2.0))
#
#        results = self.image.fit_fixed_positions(sources = [edge_posn], 
#                                       boxsize = boxsize)
##        

    def testTooCloseToEdgePosition(self):
        img = self.image
        print 
        
        boxsize = BOX_IN_BEAMPIX*max(img.beam[0], img.beam[1])
        edge_posn = img.wcs.p2s((0 + boxsize/2 -2, img.data.shape[1]/2.0))
        
#        results = self.image.fit_fixed_positions(
#                                    sources = [edge_posn], 
#                                    boxsize = boxsize,
#                                    threshold = -1e10
#                                    )
#    
#        print "Posn:", edge_posn
#        print "XY:", img.wcs.s2p(edge_posn)
#        print "Results:" , results
#        self.assertListEqual([None], results)
        with self.assertRaises(ValueError):
            results2 = self.image.fit_fixed_positions(
                                        sources = [edge_posn], 
                                        boxsize = boxsize
                                        )
            print "Results2:" , results2
        
        
        
            
#        
        
        
