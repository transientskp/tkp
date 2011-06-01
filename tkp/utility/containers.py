# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
"""
Container classes for the TKP pipeline.

These provide convenient means of marshalling the various types of data --
lightcurves, detections, sources, etc -- that the pipeline must handle.
"""

import logging
import numpy
import pylab
from ..utility.exceptions import TKPException, TKPDataBaseError


class ObjectContainer(list):
    """A container class for objects.

    What sort of objects? Well, anything that has a position and we
    want to keep lists of, really. So detections (ie, an individual
    source measurement on an image), sources (ie all the detections of
    a given object in a given image stack) and lightcurves (ie, all
    the sources associated with a given object through time).

    You probably don't want to use this on it's own: see SextractionResults,
    TargetList or source for more useful derived classes.
    """
    def closest_to(self, pix_x, pix_y):
        distance, target = False, False
        logging.debug("Beginning a search for objects near: " +
                      str(pix_x) + ", " + str(pix_y))
        logging.debug("I have %d objects" % (len(self),))
        for my_obj in self:
            my_dist = (pix_x - my_obj.x)**2 + (pix_y - my_obj.y)**2
            logging.debug("Object at %f, %f" % (my_obj.x, my_obj.y))
            logging.debug("Has distance %f" %my_dist)
            if not distance:
                distance = my_dist
                target = my_obj
            else:
                if my_dist < distance:
                    target = my_obj
                    distance = my_dist
            logging.debug("Best distance is now %f" % distance)
            logging.debug("From object " + str(target))
        if not distance:
            return (target, distance)
        else:
            return (target, distance**0.5)

    def __setslice__(self, slice, items):
        """
        Not implemented.
        """
        raise NotImplementedError

    def __iadd__(self, y):
        """
        Not implemented.
        """
        raise NotImplementedError

    def __imul__(self, y):
        """
        Not implemented.
        """
        raise NotImplementedError

    def __mul__(self, y):
        """
        Not implemented.
        """
        raise NotImplementedError

    def __rmul__(self, y):
        """
        Not implemented.
        """
        raise NotImplementedError

    def __str__(self):
        return 'Container: ' + str(len(self)) + ' object(s).'


class SextractionResults(ObjectContainer):
    """
    Container for the results of running source extraction on an ImageData
    object
    """

    def regionlist(self, radius=5):
        """Output a list of regions suitable for use in DS9.

        @type radius: Numeric
        @param radius: Size of DS9 marker object.
        """
        for o in self:
            print "circle(%f, %f, %f)" % (o.x, o.y, radius)

    def __str__(self):
        return 'SextractionResults: ' + str(len(self)) + ' detection(s).'
