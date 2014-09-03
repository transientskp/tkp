"""
Container classes for the TKP pipeline.

These provide convenient means of marshalling the various types of data --
lightcurves, detections, sources, etc -- that the pipeline must handle.
"""

import logging
logger = logging.getLogger(__name__)

class ObjectContainer(list):
    """A container class for objects.

    What sort of objects? Well, anything that has a position and we
    want to keep lists of, really. So detections (ie, an individual
    source measurement on an image), sources (ie all the detections of
    a given object in a given image stack) and lightcurves (ie, all
    the sources associated with a given object through time).

    You probably don't want to use this on it's own: see ExtractionResults,
    TargetList or source for more useful derived classes.
    """
    def closest_to(self, pix_x, pix_y):
        distance, target = False, False
        logger.debug("Beginning a search for objects near %.1f, %.1f: ",
                      pix_x, pix_y)
        logger.debug("%s contains %d objects", str(self), len(self))
        for obj in self:
            tmpdist = (pix_x - obj.x)**2 + (pix_y - obj.y)**2
            logger.debug("Object at %f, %f", obj.x, obj.y)
            logger.debug("Has distance %f", tmpdist)
            if not distance:
                distance = tmpdist
                target = obj
            else:
                if tmpdist < distance:
                    target = obj
                    distance = tmpdist
            logger.debug("Best distance is now %f", distance)
            logger.debug("From object %s", str(target))
        if not distance:
            return (target, distance)
        else:
            return (target, distance**0.5)

    def __setslice__(self, section, items):
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


class ExtractionResults(ObjectContainer):
    """Container for the results of running source extraction on an
    ImageData object"""

    def __str__(self):
        return 'ExtractionResults: ' + str(len(self)) + ' detection(s).'
