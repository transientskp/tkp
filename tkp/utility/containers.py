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

from ..utility.exceptions import TKPException, TKPDataBaseError


class ObjectContainer(list):
    """
    A container class for objects. What sort of objects? Well, anything
    that has a position and we want to keep lists of, really. So detections
    (ie, an individual source measurement on an image), sources (ie all the
    detections of a given object in a given image stack) and lightcurves (ie,
    all the sources associated with a given object through time).

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


class Source(ObjectContainer):
    """
    All the Detections associated with a given object at a certain time.
    """
    @property
    def x(self):
        """
        Mean x coordinate of all detections in this source.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.x, self, 0.0) / len(self)

    @property
    def y(self):
        """
        Mean y coordinate of all detections in this source.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.y, self, 0.0) / len(self)

    @property
    def ra(self):
        """
        Mean RA coordinate of all detections in this source.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.ra, self, 0.0) / len(self)

    @property
    def dec(self):
        """
        Mean Dec coordinate of all detections in this source.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.dec, self, 0.0) / len(self)

    @property
    def frequencybands(self):
        # This _should_ return all the frequency bands this object knows
        # about. But it doesn't. Yet.
        bands = []
        for source in self:
            bands.append(source.imagedata.freq_id)
        return list(set(bands))

    def __str__(self):
        return ('Source: ' + str(len(self)) + ' detection(s) at ' +
                str(self.x) + ',' + str(self.y))


class TargetList(ObjectContainer):
    """
    A list of all the lightcurves being monitored at a given time.
    """
    def append(self, lightcurve):
        """
        Append a new LightCurve to the list of those being monitored.

        Note that the new LightCurve i only appended if it can't be associated
        with one already being monitored. Currently, this is checked in a very
        naive way...

        @type lightcurve: L{LightCurve}
        @param lightcurve: LightCurve to monitor
        """
        if len(self) > 0:
            closest = self.closest_to(lightcurve.x, lightcurve.y)
            # Should check more intelligently for pre-existing object
            if closest < 50:
                return
        super(TargetList, self).append(lightcurve)

    def __str__(self):
        return 'TargetList: ' + str(len(self)) + ' lightcurves(s).'


class LightCurve(ObjectContainer):
    """
    A list of associated Source objects at different times.

    In other words, this provides a 2 dimensional list-based interface to a
    lightcuve. The first level, LightCurve()[n], provides access to a Source
    object describing a source at a particular time. In turn, that Source can
    be accessed as LightCurve()[n][m] to provide a detection at a given time
    and frequency.
    """
    @property
    def x(self):
        """
        Mean x coordinate of all sources in this lightcurve.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.x, self, 0.0) / len(self)

    @property
    def y(self):
        """
        Mean y coordinate of all sources in this lightcurve.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.y, self, 0.0) / len(self)

    @property
    def ra(self):
        """
        Mean RA coordinate of all detections in this source.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.ra, self, 0.0) / len(self)

    @property
    def dec(self):
        """
        Mean Dec coordinate of all detections in this source.

        Should probably do something smarter, like weighting...
        """
        return reduce(lambda x, y: x + y.dec, self, 0.0) / len(self)

    @property
    def frequencybands(self):
        bands = []
        for source in self:
            bands.append(*source.frequencybands)
        return list(set(bands))

    @property
    def ra_converted(self):
        """Returns RA as float by converting from pixel coordinates."""
        return self[0][0].wcs.p2s([self.x.value, self.y.value])[0]

    @property
    def dec_converted(self):
        """Returns Dec as float by converting from pixel coordinates."""
        return self[0][0].wcs.p2s([self.x.value, self.y.value])[1]

    def __str__(self):
        return ('Lightcurve: ' + str(len(self)) + ' source(s) at ' +
                str(self.x) + ',' + str(self.y))

    def dumpdata(self, band):
        i = 0
        for source in self:
            if source.frequencybands.count(band) > 0:
                for d in source:
                    if d.imagedata.freq_id == band:
                        print "%d\t%f\t%s" % (i, d.peak, d.layer_id)
            i += 1

    def peak(self, freq=None):
        """
        Simple way of getting lightcurve data for plotting.

        Returns image number, peak flux, and its error for each detection in
        lightcurve.

        If freq is None, assumes the lightcurve is all at one freqency and
        contains one Detection per Source.
        Otherwise, freq should be frequency identifier, and only detections
        with that freq_id will be plotted.
        """
        im_num = []
        peak = []
        peak_err = []
        for source in self:
            im_num.append(self.index(source))
            for d in source:
                if freq and not d.freq_id == freq:
                    logging.debug("Skipping detection: wrong frequency")
                    continue
                peak.append(d.peak.value)
                peak_err.append(d.peak.error)
        return numpy.array(im_num), numpy.array(peak), numpy.array(peak_err)

    def plot(self, band, graph):
        raise NotImplementedError
#        graph.reset()
#        graph.xlabel('Step')
#        graph.ylabel('Flux (Jy)')
#        data = []
#        x = []
#        i = 0
#        for source in self.objects:
#            if source.frequencybands.count(band) > 0:
#                for d in source.objects:
#                    if d.freq_id == band:
#                        data.append(d.peak)
#                        x.append(i)
#            i += 1
#
#        plot = Gnuplot.Data(x, data, title='Source', with='linespoints')
#        graph.plot(plot)


class Plots(object):

    def plotHistAssocDist(self, conn):
        """
        Not implemented
        if db.enabled == False:
            raise TKPDataBaseError("Database is not enabled")
        cursor = conn.cursor()
        try:
            # MySQL and MonetDB procedure calls are the same
            procAssoc = "CALL AssocXSourceByImage(%d)" % (imageid)
            cursor.execute(procAssoc)
        except db.Error, e:
            logging.warn("Associating image %s failed: " % (str(imageid)))
            raise
        finally:
            cursor.close()
        conn.commit()
        """
        #raise NotImplementedError
        x = pylab.randn(1000)
        pylab.hist(x)
        plotfile = 'comeupwithaname.png'
        pylab.savefig(plotfile)
        return plotfile
