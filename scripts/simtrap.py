#! /usr/bin/env python

from __future__ import division

import sys
import random
import datetime
from collections import namedtuple
from argparse import ArgumentParser
import numpy
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.font_manager import FontProperties
from matplotlib.figure import Figure
try:
    import Pycluster
except ImportError:
    raise ImportError("This script requires Pycluster: "
                      "http://bonsai.hgc.jp/~mdehoon/software/cluster/"
                      "software.htm#pycluster")
try:
    import milk
except ImportError:
    raise ImportError("This script requires milk: "
                      "http://packages.python.org/milk/")
import scipy.cluster.vq
from tkp.classification.features import lightcurve as lcmod
import tkp.database as tkpdb
import tkp.database.utils as tkpdbutils
from tkp.classification.manual import classification
import tkp.classification.manual.utils
import tkp.classification.manual.transient


def julian2greg(julianday):
    IGREG = 2299161
    jd = long(julianday)
    day = julianday - float(jd)
    if day >= 0.5:
        jd += 1
        day -= 0.5
    else:
        day += 0.5
    if jd >= IGREG:
        ialpha = long((float(jd - 1867216) - 0.25) / 36524.25)
        a = jd + 1 + ialpha - long(0.25 * ialpha)
    elif jd < 0:
        a = jd + 36525 * (1 - julianday / 36525)
    else:
        a = jd
    b = a + 1524
    c = long(6680.0 + (float(b - 2439870) - 122.1) / 365.25)
    iday = long(365 * c + (0.25 * c))
    e = long((b - iday) / 30.6001)
    iday = b - iday - long(30.6001 * e)
    imonth = e - 1
    if imonth > 12:
        imonth = imonth - 12
    iyear = c - 4715
    if imonth > 2:
        iyear -= 1
    if iyear <= 0:
        iyear -= 1
    if jd < 0:
        iyear -= 100 * (1 - jd / 36525)
    # Parse the day into hour, minute, second
    hour, minute = divmod(day * 24, 1)
    minute, second = divmod(minute * 60, 1)
    second *= 60
    hour = int(hour)
    minute = int(minute)
    microsecond = int((second - int(second)) * 1e6)
    date = datetime.datetime(
        iyear, imonth, iday, int(hour), int(minute), int(second),
        int(microsecond))
    return date


class Dataset(object):

    def __init__(self, name, images=None):
        self.name = name
        self.images = images[:] if images else []

    def __str__(self):
        return "Dataset %s" % self.name

    def __repr__(self):
        return "Dataset(name=%s, images=%s)" % (
            self.name, repr(self.images))


class Position(object):

    def __init__(self, ra, dec, error_ra=0., error_dec=0.):
        self.ra = ra
        self.dec = dec
        self.error_ra = error_ra
        self.error_dec = error_dec

    def __str__(self):
        return "(%g, %g)" % (self.ra, self.dec)

    def __repr__(self):
        return "Position(ra=%g, dec=%g, error_ra=%g, error_dec=%g)" % (
            self.ra, self.dec, self.error_ra, self.error_dec)

    
class Flux(object):

    def __init__(self, I, Q=0, U=0., V=0.):
        self.I = I
        self.Q = Q
        self.U = U
        self.V = V
        self.stokes = (I, Q, U, V)

    def __str__(self):
        return "[%g, %g, %g, %g]" % self.stokes

    
    def __repr__(self):
        return "Flux(I=%g, Q=%g, U=%g, V=%g" % self.stokes
            

class Image(object):

    @classmethod
    def from_observation(self, field, observation, timeresolution=10, inttime=None):
        """Calculate the source flux levels and background rms for an image
        """

        
        if inttime is None:
            inttime = observation.inttime
        obsdates = (numpy.arange(0, inttime,
                                 timeresolution)/86400. + observation.obsdate)
        detected_sources = []
        for source in field.sources:
            flux = source.lightcurve.flux(obsdates)
            detected_sources.append(
                DetectedSource(position=source.position,
                               lightcurve=source.lightcurve,
                               transient=source.transient,
                               flux=flux.mean()))
        rms = observation.configuration.rms / inttime
        return Image(obsdate=observation.obsdate, inttime=inttime,
                     sources=detected_sources, pointing=field.pointing,
                     fov=(field.radius, field.radius), rms=rms)

    def __init__(self, obsdate, inttime, sources=None,
                 pointing=None, fov=None, rms=0.):
        self.obsdate = obsdate
        self.inttime = inttime
        self.sources = sources[:] if sources else []
        self.pointing = pointing if pointing else Position(0, 0)
        self.fov = fov if fov else (0., 0.)   # arcminutes
        self.rms = rms
        
    def __str__(self):
        return ("Image with %g rms, taken at %s (%d seconds), at %s "
                "(%.1f x %.1f arcmin FoV), containg %d sources" % (
            self.rms, str(self.obsdate), int(self.inttime), str(self.pointing),
            self.fov[0], self.fov[1], len(self.sources)))

    def __repr__(self):
        return ("Image(obsdate=%s, inttime=%g, sources=%s, pointing=%s, "
                "fov=%s, rms=%g" % (
            repr(self.obsdate), self.inttime, repr(self.sources), repr(self.pointing),
            repr(self.fov), self.rms))


class AntennaConfiguration(object):
    """Class that defines an antenna configuration.

    The antenna configuration sets things like the resolution and background level.

    """

    CS001 = (0, 0)
    CS002 = (1, 0)
    CS003 = (0, 1)
    CS004 = (-1, 0)
    CS005 = (0, -1)
    CS010 = (10, 0)
    CS011 = (0, 10)
    CS012 = (7, 7)
    CS013 = (-5, -8)
    CS014 = (8, -5)
    CS015 = (-8, 5)
    CS016 = (5, 8)
    CS100 = (50, 0)
    CS101 = (50, 50)
    CS102 = (35, 35)
    CS103 = (-35, -35)

    BASE_RMS = 1e-2
    
    def __init__(self, antennas=None):
        self.antennas = antennas[:] if antennas else self._set_default()
        self.resolution = self.calc_resolution()
        self.rms = self.calc_rms()

    def _set_default(self):
        antennas = [
            AntennaConfiguration.CS001,
            AntennaConfiguration.CS002,
            AntennaConfiguration.CS003,
            AntennaConfiguration.CS004,
            AntennaConfiguration.CS005,
            AntennaConfiguration.CS010,
            AntennaConfiguration.CS011,
            AntennaConfiguration.CS012,
            AntennaConfiguration.CS013,
            AntennaConfiguration.CS014,
            AntennaConfiguration.CS015,
            AntennaConfiguration.CS016,
            AntennaConfiguration.CS100,
            AntennaConfiguration.CS101,
            AntennaConfiguration.CS102,
            AntennaConfiguration.CS103,
            ]
        return antennas

    def calc_resolution(self):
        """Calculate the resolution from the maximum distance between
        antennas"""
        maxdist = 0.
        for i, ant1 in enumerate(self.antennas):
            for j, ant2 in enumerate(self.antennas[i:]):
                dist = numpy.sqrt((ant1[0] - ant2[0])**2 +
                                  (ant1[1] - ant2[1])**2)
                if dist > maxdist:
                    maxdist = dist 
        return 1./maxdist

    def calc_rms(self):
        """Calculate the background RMS from the number of antennas used.
        Assume all stations equally sensitive"""
        rms = AntennaConfiguration.BASE_RMS/numpy.sqrt(len(self.antennas))
        return rms
                    
            
class Field(object):

    @classmethod
    def create_random(self, pointing_range=((0., 360.), (-90., 90.)),
                      radius_range=(0., 90.), nsources_range=(0, 1),
                      position_error=(0., 0.), flux_range=(0., 1.),
                      timerange=(0., 1.),
                      transients_percentage=0., with_background=True):
        ra = random.uniform(*(pointing_range[0]))
        dec = random.uniform(*(pointing_range[1]))
        radius = random.uniform(*radius_range)
        nsources = random.randint(*nsources_range)
        sources = []
        position_range = ((ra-radius, ra+radius), (dec-radius, dec+radius))
        for i in range(nsources):
            source = Source.create_random(
                position_range=position_range, position_error=position_error,
                timerange=timerange)
            if random.random() > transients_percentage:
                source.lightcurve = ConstantLC(
                    peak=random.uniform(*flux_range))
            elif with_background:
                if not isinstance(source.lightcurve, ConstantLC):
                    background = ConstantLC(
                        peak=random.uniform(flux_range[0]/10.,
                                             flux_range[1]/10.))
                    source.lightcurve = CombinedLightCurve(
                        [source.lightcurve, background])
            sources.append(source)
        return Field(pointing=Position(ra, dec), radius=radius,
                     sources=sources)
        
    def __init__(self, pointing=None, radius=0., sources=None):
        self.pointing = pointing if pointing else Position(0, 0)
        self.radius = radius
        self.sources = sources[:] if sources else []

    def __str__(self):
        return "Field with %d sources  pointed at (%g, %g)" % (
            len(self.sources), self.pointing.ra, self.pointing.dec)

    def __repr__(self):
        return "Field(pointing=%s, radius=%g, sources=%s" % (
            repr(self.pointing), self.radius, repr(self.sources))


class Observation(object):

    def __init__(self, obsdate, inttime, configuration=None):
        self.obsdate = obsdate
        self.inttime = inttime
        self.configuration = configuration 
        if self.configuration is None:
            self.configuration = AntennaConfiguration()

    def observe(self, field, peakflux_range=(1., 2.)):
        pass
    
    def __str__(self):
        return "Observation starting at %s for %d seconds" % (
            self.obsdate, self.inttime)

    def __repr__(self):
        return "Observation(obsdate=%s, inttime=%g)" % (
            repr(self.obsdate), self.inttime)
    
    
class Source(object):

    @classmethod
    def create_random(cls, position_range=((0, 360), (-90, 90)),
                      position_error=(0., 0.),
                      flux_range=(0, 1), lctypes=None,
                      timerange=(0, 1)):
        ra = random.uniform(*(position_range[0]))
        dec = random.uniform(*(position_range[1]))
        error_ra = position_error[0]
        error_dec = position_error[1]
        position = Position(ra, dec, error_ra, error_dec)
        #flux = Flux(I=random.uniform(*flux_range))
        if lctypes is None:
            lctypes = (ConstantLC, GaussLC, TriangleLC, DoubleGaussLC,
                       LogTriangleLC, LorentzLC, FredLC, ChaosLC)
        lctype = random.choice(lctypes)
        lightcurve = lctype.create_random(timerange=timerange)
        #lightcurve = ConstantLC()
        return Source(position=position, lightcurve=lightcurve)

    def __init__(self, position, lightcurve=None, transient=False):
        self.position = position
        self.lightcurve = lightcurve if lightcurve else ConstantLC()
        self.transient = transient

    def set_lightcurve(self, obstimes, inttimes, peak, center, width,
                       start, end):
        self.lightcurve = self.lctype(obstimes, inttimes, peak, center, width,
                                      start, end)
            
    def __str__(self):
        return "Source at (%g, %g) with lightcurve %s" % (
            self.position.ra, self.position.dec, self.lightcurve)

    def __repr__(self):
        return "Source(position=%s, lightcurve=%s, transient=%s)" % (
            repr(self.position), repr(self.lightcurve), repr(self.transient))


class DetectedSource(Source):

    @classmethod
    def from_observation(self, source, observation, timeresolution=10):
        """Calculate the flux levels for a specific source
        """

        flux = 0.
        obsdates = numpy.arange(0, observation.inttime, timeresolution)/86400. + observation.obsdate
        flux = source.lightcurve.flux(obsdates)
        return DetectedSource(position=source.position,
                              lightcurve=source.lightcurve,
                              transient=source.transient,
                              flux=flux)

    def __init__(self, *args, **kwargs):
        self.flux = kwargs.pop('flux', numpy.zeros(0,))
        super(DetectedSource, self).__init__(*args, **kwargs)
        
    def __str__(self):
        return "Detected source at (%g, %g) with average flux %g" % (
            self.position.ra, self.position.dec, self.flux.mean())

    

class LightCurve(object):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        """Dummy implementation"""
        return LightCurve()

    def __init__(self, *args, **kwargs):
        pass

    def _flux(self, flux, obsdate):
        if isinstance(obsdate, numpy.ndarray):
            return flux * numpy.ones(obsdate.shape)
        else:
            return flux
        
    def flux(self, obsdate):
        return self._flux(0., obsdate)
    
    def __str__(self):
        return "Default light curve"
    

class ConstantLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        peak = random.uniform(*kwargs.get('peakrange', (0., 1.)))
        return ConstantLC(peak)

    def __init__(self, *args, **kwargs):
        self.peak = kwargs.pop('peak', 1.)
        super(ConstantLC, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Constant lightcurve"

    def __repr__(self):
        return "ConstantLC(peak=%g)" % self.peak
    
    def flux(self, obsdate):
        return self._flux(self.peak, obsdate)


class GaussLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        center = random.uniform(*timerange)
        delta = timerange[1] - timerange[0]
        width = random.uniform(*kwargs.pop('widthrange', (0., delta)))
        peak = random.uniform(*kwargs.pop('peakrange', (0., 1.)))
        return GaussLC(center=center, width=width, peak=peak)

    def __init__(self, *args, **kwargs):
        self.center = kwargs.pop('center', 0.)
        self.width = kwargs.pop('width', 1.)
        self.peak = kwargs.pop('peak', 1.)
        super(GaussLC, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Gaussian lightcurve"

    def __repr__(self):
        return "GaussLC(center=%g, width=%g, peak=%g)" % (
            self.center, self.width, self.peak)
    
    def flux(self, obsdate):
        flux = self.peak * numpy.exp(- ((obsdate - self.center)**2 / (2 * self.width**2)))
        return flux


class DoubleGaussLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        center1 = random.uniform(*timerange)
        delta = timerange[1] - timerange[0]
        width1 = random.uniform(*kwargs.pop('widthrange', (0., delta)))
        peak1 = random.uniform(*kwargs.pop('peakrange', (0., 1.)))
        center2 = random.uniform(*timerange)
        delta = timerange[1] - timerange[0]
        width2 = random.uniform(*kwargs.pop('widthrange', (0., delta)))
        peak2 = random.uniform(*kwargs.pop('peak2range', (0., 1.)))
        return DoubleGaussLC(center=(center1, center2),
                             width=(width1, width2),
                             peak=(peak1, peak2))

    def __init__(self, *args, **kwargs):
        self.center = kwargs.pop('center', (0.5, 0.5))
        self.width = kwargs.pop('width', (1., 1.))
        self.peak = kwargs.pop('peak', (1., 1.))
        super(DoubleGaussLC, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Double Gaussian lightcurve"

    def __repr__(self):
        return "DoubleGaussLC(center=%s, width=%s, peak=%s)" % (
            repr(self.center), repr(self.width), repr(self.peak))
    
    def flux(self, obsdate):
        flux = self.peak[0] * numpy.exp(- ((obsdate - self.center[0])**2 / (2 * self.width[0]**2)))
        flux += self.peak[1] * numpy.exp(- ((obsdate - self.center[1])**2 / (2 * self.width[1]**2)))
        return flux


class TriangleLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        start = random.uniform(*timerange)
        end = random.uniform(*kwargs.pop('endrange', (start, timerange[1])))
        mode = random.uniform(start, end)
        peak = random.uniform(*kwargs.pop('peakrange', (0., 1.)))
        return TriangleLC(start=start, end=end, mode=mode, peak=peak)

    def __init__(self, *args, **kwargs):
        self.start = kwargs.pop('start', 0.)
        self.end = kwargs.pop('end', 1.)
        self.mode = kwargs.pop('mode', 0.5)
        self.peak = kwargs.pop('peak', 1.)
        super(TriangleLC, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Triangular lightcurve"

    def __repr__(self):
        return "TriangleLC(start=%g, end=%g, mode=%g, peak=%g)" % (
            self.start, self.end, self.mode, self.peak)

    def flux(self, obsdate):
        if isinstance(obsdate, numpy.ndarray):
            flux = numpy.zeros(obsdate.shape)
            indices = (self.start < obsdate) & (obsdate < self.mode)
            flux[indices] = self.peak * (obsdate[indices] - self.start) / (self.mode - self.start)
            indices = (self.mode < obsdate) & (obsdate < self.end)
            flux[indices] = self.peak * (self.end - obsdate[indices]) / (self.end - self.mode)
        else:
            flux = 0.
            if self.start < obsdate < self.mode:
                flux = self.peak * (obsdate - self.start) / (self.mode - self.start)
            elif self.mode < obsdate < self.end:
                flux = self.peak * (self.end - obsdate) / (self.end - self.mode)
        return flux

class LogTriangleLC(TriangleLC):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        start = random.uniform(*timerange)
        end = random.uniform(*kwargs.pop('endrange', (start, timerange[1])))
        mode = random.uniform(start, end)
        peak = random.uniform(*kwargs.pop('peakrange', (0., 1.)))
        return LogTriangleLC(start=start, end=end, mode=mode, peak=peak)

    def __init__(self, *args, **kwargs):
        super(LogTriangleLC, self).__init__(*args, **kwargs)
        
    def __str__(self):
        return "Logarithmic triangular lightcurve"

    def __repr__(self):
        return "LogTriangleLC(start=%g, end=%g, mode=%g, peak=%g)" % (
            self.start, self.end, self.mode, self.peak)

    def flux(self, obsdate):
        flux = super(LogTriangleLC, self).flux(obsdate)
        flux = 9 * flux/self.peak + 1
        flux = self.peak * numpy.log10(flux)
        return flux
    

class Block(object):

    pass


class Curve(object):

    pass


class LorentzLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        center = random.uniform(*timerange)
        delta = timerange[1] - timerange[0]
        width = random.uniform(*kwargs.pop('widthrange', (0., delta)))
        peak = random.uniform(*kwargs.pop('peakrange', (0., 1.)))
        return LorentzLC(peak=peak, center=center, width=width)

    def __init__(self, *args, **kwargs):
        self.peak = kwargs.pop('peak')
        self.center = kwargs.pop('center')
        self.width = kwargs.pop('width')
        super(LorentzLC, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Lorentzian lightcurve"

    def __repr__(self):
        return "Lorentz(center=%g, width=%g, peak=%g)" % (
            self.center, self.width, self.peak)
    
    def flux(self, obsdate):
        flux = ((0.5 * self.width) / ((obsdate - self.center)**2 + 0.25 *
                                      self.width**2))
        flux *= self.peak / numpy.pi
        return flux


class FredLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        start = random.uniform(*timerange)
        scale = random.uniform(*kwargs.pop('scale', (1, 10.)))
        power = random.uniform(*kwargs.pop('power', (0.1, 10.)))
        exp = random.uniform(*kwargs.pop('scale', (0, timerange[1]-timerange[0])))
        peak = random.uniform(*kwargs.pop('peakrange', (0., 1.)))
        return FredLC(power=power, exp=exp, scale=scale, start=start,
                      peak=peak)

    def __init__(self, *args, **kwargs):
        self.power = kwargs.pop('power', 1.)
        self.exp = kwargs.pop('exp', 1.)
        self.scale = kwargs.pop('scale', 10.)
        self.start = kwargs.pop('start', 0.)
        self.peak = kwargs.pop('peak', 1.)
        super(FredLC, self).__init__(*args, **kwargs)

    def __str__(self):
        return "Fred lightcurve"

    def __repr__(self):
        return "FredLC(power=%g, exp=%g, scale=%g, start=%g, peak=%g)" % (
            self.power, self.exp, self.scale, self.start, self.peak)
    
    def flux(self, obsdate):
        x = (obsdate - self.start) / self.scale
        if isinstance(obsdate, numpy.ndarray):
            flux = numpy.zeros(obsdate.shape)
            indices = x > 0.
            flux[indices] = x[indices] ** self.power
            indices = flux > 1
            flux[indices] = numpy.exp(-self.exp * (x[indices]-1))
        else:
            if x < 0:
                return 0.
            flux = x ** self.power
            if flux > 1:
                flux = numpy.exp(-self.exp * (x-1))
        flux *= self.peak
        return flux
                                                                
        
class ChaosLC(LightCurve):

    @classmethod
    def create_random(self, timerange=(0, 1), **kwargs):
        start = random.uniform(*timerange)
        scale = random.uniform(*kwargs.pop('scale', (0.1, 1.)))
        mindur = random.uniform(*kwargs.pop('mindur', (0., 0.5*timerange[1])))
        maxdur = random.uniform(*kwargs.pop('maxdur', (mindur, timerange[1])))
        variability = random.uniform(*kwargs.pop(
            'variability', (timerange[1]/100., timerange[1]/10.)))
        return ChaosLC(start=start, scale=scale, mindur=mindur, maxdur=maxdur)

    def __init__(self, *args, **kwargs):
        self.start = kwargs.pop('start', 0.)
        self.scale = kwargs.pop('scale', 1.)
        self.mindur = kwargs.pop('mindur', 1.)
        self.maxdur = kwargs.pop('maxdur', 1.)
        self.variability = kwargs.pop('variability', 0.1)
        super(ChaosLC, self).__init__(*args, **kwargs)
        self.prevflux = 0.
        self.change_percentage = 0.3
        self.obsdates, self.fluxes = self._calc_curve()
        
    def __str__(self):
        return "Chaotic lightcurve"

    def __repr__(self):
        return "ChaosLC(start=%g, scale=%g, mindur=%g, maxdur=%g)" % (
            self.start, self.scale, self.mindur, self.maxdur)

    def _calc_curve(self):
        obsdates = numpy.arange(self.start, self.start+self.maxdur, self.variability)
        change_percentage = self.change_percentage * numpy.sin(
            (obsdates.mean()-self.start)/self.maxdur*numpy.pi)
        shape = obsdates.shape
        scale = self.scale * numpy.ones(shape)
        scale = numpy.random.uniform(0.1*scale, scale)
        # fix oddity in numpy.random.uniform output        
        if isinstance(scale, float):
            scale = numpy.array([scale])
        change = numpy.zeros(shape)
        random = numpy.random.random(shape)
        # Overall increasing part
        indices = obsdates < self.start + self.mindur
        increase = scale[indices]
        # But occasionally decrease the flux
        indices2 = random[indices] < change_percentage
        increase[indices2] = -scale[indices2]
        change[indices] = increase
        # Overall decreaseing part
        decrease = -scale[-indices]
        # But occasionally increase flux
        indices2 = random[-indices] < change_percentage
        decrease[indices2] = scale[indices2]
        change[-indices] = decrease
        L = len(change)
        fluxes = numpy.sum(numpy.tril(numpy.ones((L, L))) * change, 1)
        fluxes[fluxes < 0.] = 0.
        return obsdates, fluxes

    def _flux(self, date):
        if date < self.obsdates[0] or date > self.obsdates[-1]:
            flux = 0.
        else:
            L = len(self.obsdates)
            argmin = abs(date - self.obsdates).argmin()
            if argmin == 0:
                argtwo = 1
            elif argmin == L-1:
                argtwo = L-2
            elif (abs(self.obsdates[argmin-1] - date) <
                  abs(self.obsdates[argmin+1] - date)):
                argtwo = argmin-1
            else:
                argtwo = argmin+1
            delta = ((self.fluxes[argtwo] - self.fluxes[argmin]) /
                     (self.obsdates[argtwo] - self.fluxes[argmin]))
            flux = (date - self.obsdates[argmin]) * delta + self.fluxes[argmin]
        return flux
    
    def flux(self, obsdate):
        if isinstance(obsdate, numpy.ndarray):
            flux = numpy.zeros(obsdate.shape)
            for i, date in enumerate(obsdate):
                flux[i] = self._flux(date)
            self.prevflux = flux
        else:
            if obsdate < self.start or obsdate > self.start+self.maxdur:
                return 0.
            change_percentage = self.change_percentage * numpy.sin(
                (obsdate-self.start)/self.maxdur*numpy.pi)
            change = random.uniform(0.1*self.scale, self.scale)
            if obsdate < self.start+self.mindur:  # largely increasing light curve
                if random.random() > self.change_percentage:
                    change = -change
            elif random.random() > 1-self.change_percentage:
                change = -change
            flux = self.prevflux + change
            if flux < 0:
                flux = 0.
        self.prevflux = flux
        return flux


class CombinedLightCurve(object):

    def __init__(self, sources):
        self.sources = sources

    def __str__(self):
        return " + ".join([str(source) for source in self.sources])

    def __repr__(self):
        return "CombinedLightCurve([%s])" % ", ".join(
            [repr(source) for source in self.sources])

    def flux(self, obsdate):
        return sum([source.flux(obsdate) for source in self.sources])


def gauss(obstimes, inttimes, center, width, peak, bglevel, noise):
    lightcurve = (Constant(obstimes=obstimes, inttimes=inttimes, level=bglevel,
                           noise=noise) +
                  Gauss(obstimes=obstimes, inttimes=inttimes, noise=0.,
                        center=center, width=width, peak=peak))
    return lightcurve


def doublegauss(obstimes, inttimes, center, width, peak, bglevel, noise):
    lightcurve = (Constant(obstimes=obstimes, inttimes=inttimes, level=bglevel,
                           noise=noise) +
                  DoubleGauss(obstimes=obstimes, inttimes=inttimes, noise=0.,
                              center=center, width=width, peak=peak))
    return lightcurve


def triangle(obstimes, inttimes, low, high, mode, peak, bglevel, noise,
             log=False):
    if log:
        lightcurve = LogTriangle(obstimes=obstimes, inttimes=inttimes, noise=0.,
                                 start=low, end=high, mode=mode, peak=peak)
    else:
        lightcurve = Triangle(obstimes=obstimes, inttimes=inttimes, noise=0.,
                              start=low, end=high, mode=mode, peak=peak)
    lightcurve += Constant(obstimes=obstimes, inttimes=inttimes, level=bglevel,
                           noise=noise)
    return lightcurve


def lorentz(obstimes, inttimes, center, width, peak, bglevel, noise):
    lightcurve = (Constant(obstimes=obstimes, inttimes=inttimes, level=bglevel,
                           noise=noise) +
                  Lorentz(obstimes=obstimes, inttimes=inttimes, noise=0.,
                          center=center, width=width, peak=peak))
    return lightcurve


def fred(obstimes, inttimes, power, exp, duration, start,  peak, bglevel, noise):
    lightcurve = (Constant(obstimes=obstimes, inttimes=inttimes, level=bglevel,
                           noise=noise) +
                  Fred(obstimes=obstimes, inttimes=inttimes, noise=0.,
                       power=power, exp=exp, duration=duration, start=start,
                       peak=peak))
    return lightcurve


def chaos(obstimes, inttimes, start, end, mindur, maxdur, delta, bglevel, noise):
    lightcurve = (Constant(obstimes=obstimes, inttimes=inttimes, level=bglevel,
                           noise=noise) +
                  Chaos(obstimes=obstimes, inttimes=inttimes, noise=0.,
                        start=start, mindur=mindur, maxdur=maxdur, delta=delta))
    return lightcurve


def background_distribution(inttime):
    """Pick a background noise level uniformly in a (small) range.
    The noise level decreases with integration time
    """
    LOW, HIGH = 1e-5, 5e-5
    level = random.uniform(LOW, HIGH) / numpy.sqrt(inttime)
    return level


def create_random(percentage, start, end, interval, inttime, background):
    CHOICES = ['gauss', 'gauss', 'doublegauss', 'triangle', 'logtriangle',
               'lorentz', 'fred', 'chaos',]
    obstimes = numpy.arange(start, end, interval)
    inttimes = inttime * numpy.ones(obstimes.shape)
    if random.random() < percentage:
        lightcurve = Constant(obstimes=obstimes, inttimes=inttimes,
                              noise=background['noise'],
                              level=background['level'])
        lightcurve.type = 'constant'
        return lightcurve
    choice = random.choice(CHOICES)
    #choice = 'logtriangle'
    peak = background['level'] * random.triangular(5, 100, 30)
    if choice == 'gauss':
        center = random.uniform(start+interval, end-interval)
        width = random.uniform(0.5*interval, 10*interval)
        lightcurve = gauss(obstimes, inttimes, center, width, peak,
                           background['level'], background['noise'])
    elif choice == 'doublegauss':
        center = [random.uniform(start+interval, end-interval), 0]
        width = (random.uniform(0.5*interval, 10*interval),
                 random.uniform(0.5*interval, 10*interval))
        center = (center[0],
                  random.uniform(center[0] - 3*width[0] - 3*width[1],
                                 center[0] + 3*width[0] + 3*width[1]))
        lightcurve = doublegauss(obstimes, inttimes, center, width,
                                 (peak, peak),
                                 background['level'], background['noise'])
    elif choice in ('triangle', 'logtriangle'):
        low = random.uniform(start, end-interval)
        high = random.uniform(low, end)
        mode = random.uniform(low+interval, high-interval)
        log = False if choice == triangle else True
        lightcurve = triangle(obstimes, inttimes, low, high, mode, peak/10.,
                              background['level'], background['noise'],
                              log=log)
    elif choice == 'lorentz':
        center = random.uniform(start+interval, end-interval)
        width = random.uniform(0.5*interval, 2*interval)
        lightcurve = lorentz(obstimes, inttimes, center, width, peak,
                             background['level'], background['noise'])
    elif choice == 'fred':
        power = random.uniform(0.3, 1.2)
        exp = random.uniform(0.5, 2.)
        duration = random.uniform(1., 1+(end-start)/2.)
        start = random.uniform(start, (start + end)/2.)
        lightcurve = fred(obstimes, inttimes, power, exp, duration, start,
                          peak, background['level'], background['noise'])
    elif choice == 'chaos':
        delta = end-start
        start = random.uniform(start, start + delta/2.)
        mindur = random.uniform(obstimes[2]-obstimes[0], 0.5*delta)
        maxdur = random.uniform(mindur + 0.1*delta, mindur + 0.5*delta)
        delta = peak/10.
        lightcurve = chaos(obstimes, inttimes, start, end, mindur, maxdur, delta,
                           background['level'], background['noise'])
    lightcurve.type = choice
    return lightcurve


def create(number, percentage):
    lightcurves = []
    background = {'level': 0, 'noise': 0}
    for i in xrange(number):
        start = 2455000
        end = random.uniform(start+50, start+200)
        interval = (end-start) / random.uniform(50, 150)
        inttime = random.expovariate(1./1800)
        inttime = 600 if inttime < 600 else inttime
        inttime = 7200 if inttime > 7200 else inttime
        background['noise'] = background_distribution(inttime)
        background['level'] = background['noise'] * random.uniform(1, 1e3)
        lightcurves.append(create_random(1-percentage, start, end, interval,
                                         inttime, background))
    return lightcurves


def plot(lightcurve, filename, plot_transients=False, separate=False):
    figure = Figure()
    if separate and isinstance(lightcurve, list):
        n = len(lightcurve)
        if plot_transients:
            n = 0
            for lc in lightcurve:
                if lc.type != 'constant':
                    n += 1
        m = int(numpy.sqrt(n))
        n = int(numpy.ceil(n / m))
    else:
        axes = figure.add_subplot(1, 1, 1)
        axes.set_yscale('log')
    if isinstance(lightcurve, list):
        i = 1
        for lc in lightcurve:
            if lc.type == 'constant' and plot_transients:
                continue
            if separate:
                axes = figure.add_subplot(n, m, i)
                axes.set_yscale('log')
                axes.errorbar(lc.obstimes, lc.fluxes,
                              lc.errors, lc.inttimes/2./86400.)
                axes.set_title(str(i))
                i += 1
            else:
                axes.errorbar(lc.obstimes, lc.fluxes,
                              lc.errors, lc.inttimes/2./86400.)
    else:
        axes.errorbar(lightcurve.obstimes, lightcurve.fluxes,
                      lightcurve.errors, lightcurve.inttimes/2./86400.)
    if isinstance(filename, basestring):
        canvas = FigureCanvas(figure)
        canvas.print_figure(filename)
    else:
        filename.savefig(figure)


def parse_options():
    parser = ArgumentParser(description="")
    parser.add_argument("-n", "--number", type=int, default=10,
                        help=("Number of simulated light curves "
                              "(default %(default)s)"))
    parser.add_argument("-c", "--percentage", type=float, default=0.2,
                        help="""\
Percentage (between 0 and 1) of light curves that are transient
(default %(default)s).""")
    parser.add_argument("-k", type=int, default=5,
                        help="Number of centroids (default %(default)s)")
    parser.add_argument("--no-print", action='store_true',
                        default=False,
                        help="Do no print any characteristics of light curves")
    parser.add_argument("--print-transients", action='store_true',
                        help="Print only the characteristics of transients")
    parser.add_argument("-p", "--plot", action='store_true',
                        help="Plot light curves")
    parser.add_argument("--plot-transients", action='store_true',
                        help="Plot only the transient light curves")
    parser.add_argument("--plot-separate", action='store_true',
                        help="Plot every light curve separately")
    args = parser.parse_args()
    return args


def cluster(transients, k):
    print '\nClustering\n========\n'
    print transients.shape, k
    transients = numpy.array(transients)
    transients_norm = scipy.cluster.vq.whiten(transients)
    while True:
        try:
            normalization = transients[0]/transients_norm[0]
            break
        except RuntimeWarning, exc:  # division by zero
            print exc
    centroids, distortion = scipy.cluster.vq.kmeans(transients_norm, k)
    print 'kmeans:', centroids
    print distortion
    centroids, labels = scipy.cluster.vq.kmeans2(transients_norm, k)
    # Denormalise
    centroids *= normalization
    print 'kmeans2:', centroids
    print labels
    return centroids, labels


def plotmap(transients, axes=((0, 'axes 0'), (1, 'axes 1')), centroids=None, labels=None,
            filename='cluster.png', title=''):
    figure = Figure()
    fig_axes = figure.add_subplot(1, 1, 1)
    x, y = transients[:, axes[0][0]], transients[:, axes[1][0]]
    if centroids is not None:
        if labels is not None:
            colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff',
                      '#00ffff', '#990000', '#009900', '#000099', '#999900',
                      '#990099', '#009999']
            icolor = 0
            ncolors = len(colors)
            for label in numpy.unique(labels):
                selection = (labels == label)
                fig_axes.scatter(x[selection], y[selection], c=colors[icolor])
                icolor = 0 if icolor == ncolors else icolor + 1
            x, y = centroids[:, axes[0][0]], centroids[:, axes[1][0]]
            fig_axes.scatter(x, y, c='0.5', marker='8', s=150)
        else:
            # Plot transients in a single color
            fig_axes.scatter(x, y, c='g')
            # Plot the centroids in adifferent color
            x, y = centroids[:, axes[0][0]], centroids[:, axes[1][0]]
            fig_axes.scatter(x, y, c='0.5', marker='8', s=150)
    else:
        # Plot transients
        fig_axes.scatter(x, y)
    fig_axes.set_title(title)
    fig_axes.set_xlabel(axes[0][1])
    fig_axes.set_ylabel(axes[1][1])
    canvas = FigureCanvas(figure)
    if isinstance(filename, basestring):
        canvas.print_figure(filename)
    else:
        filename.savefig(figure)
    


def plotmaps(transients, axes=[((0, 'axes 0'), (1, 'axes 1'))], centroids=None,
             labels=None, filename='clusters.png', title=''):
    figure = Figure()
    N = len(axes)
    m = int(numpy.sqrt(N))
    n = int(numpy.ceil(N / m))
    for i in range(N):
        fig_axes = figure.add_subplot(n, m, i)        
        x, y = transients[:, axes[i][0][0]], transients[:, axes[i][1][0]]
        if centroids is not None:
            if labels is not None:
                colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff',
                          '#00ffff', '#990000', '#009900', '#000099', '#999900',
                          '#990099', '#009999']
                icolor = 0
                ncolors = len(colors)
                for label in numpy.unique(labels):
                    selection = (labels == label)
                    fig_axes.scatter(x[selection], y[selection], c=colors[icolor])
                    icolor = 0 if icolor == ncolors else icolor + 1
                x, y = centroids[:, axes[i][0][0]], centroids[:, axes[i][1][0]]
                fig_axes.scatter(x, y, c='0.5', marker='8', s=150)
            else:
                # Plot transients in a single color
                fig_axes.scatter(x, y, c='g')
                # Plot the centroids in adifferent color
                x, y = centroids[:, axes[i][0][0]], centroids[:, axes[i][1][0]]
                fig_axes.scatter(x, y, c='0.5', marker='8', s=150)
        else:
            # Plot transients
            fig_axes.scatter(x, y)
        fig_axes.set_xlabel(axes[i][0][1])
        fig_axes.set_ylabel(axes[i][1][1])
    figure.suptitle(title)
    canvas = FigureCanvas(figure)
    if isinstance(filename, basestring):
        canvas.print_figure(filename)
    else:
        filename.savefig(figure)

    
def main():
    datasets = simulate_datasets()
    database = tkpdb.DataBase()
    ids = store_datasets(datasets, database)
    sources = get_transients(ids, database)
    transients = extract_features(sources)
    database.close()
    
    
def simulate_datasets():
    pos1 = Position(123.123, 45.45, 5./3600., 5./3600.)
    flux1 = Flux(23.)
    src1 = Source(position=pos1)
    pos2 = Position(234.234, 56.56, 6./3600., 6./3600.)
    flux2 = Flux(46.)
    src2 = Source(position=pos2, transient=True)
    position_range=((100., 110.), (40., 50.))
    src3a = Source.create_random(position_range=position_range)
    src3b = Source.create_random(position_range=position_range)
    src3c = Source.create_random(position_range=position_range)
    field1 = Field(pointing=Position(23, -23), radius=5.,
                   sources=[src1, src2, src3a])
    field2 = Field(pointing=Position(105., 45.), radius=5.,
                   sources=[src3a, src3b, src3c])
    field3 = Field.create_random(
        pointing_range=((20., 40.), (30., 40.)), radius_range=(5., 7.),
        nsources_range=(10, 15), position_error=(5./3600., 5./3600.),
        flux_range=(10., 20.))
    field4 = Field.create_random(
        pointing_range=((20., 40.), (30., 40.)), radius_range=(5., 7.),
        nsources_range=(5, 15), position_error=(5./3600., 5./3600.),
        timerange=(0., 50.),
        flux_range=(1e-5, 1e-3), transients_percentage=.2)

    lcs = [ConstantLC.create_random(),
          GaussLC.create_random(timerange=(8., 100.)),
          DoubleGaussLC.create_random(timerange=(8., 100.)),
          TriangleLC.create_random(timerange=(8., 100.)),
          LogTriangleLC.create_random(timerange=(8., 100.)),
          LorentzLC.create_random(timerange=(8., 100.)),
          ChaosLC.create_random(timerange=(8., 100.)),
          GaussLC.create_random(timerange=(8., 100.)),
          DoubleGaussLC.create_random(timerange=(8., 100.)),
          TriangleLC.create_random(timerange=(8., 100.)),
          LogTriangleLC.create_random(timerange=(8., 100.)),
          LorentzLC.create_random(timerange=(8., 100.)),
          ChaosLC.create_random(timerange=(8., 100.)),
          GaussLC.create_random(timerange=(8., 100.)),
          DoubleGaussLC.create_random(timerange=(8., 100.)),
          TriangleLC.create_random(timerange=(8., 100.)),
          LogTriangleLC.create_random(timerange=(8., 100.)),
          LorentzLC.create_random(timerange=(8., 100.)),
          ChaosLC.create_random(timerange=(8., 100.))]
    n = len(lcs)
    m = int(numpy.sqrt(n))
    n = int(numpy.ceil(n / m))
    obsdates = numpy.arange(0, 100., 0.1)
    fluxes = []  #numpy.zeros(obsdates.shape)
    for nsubplot, lc in enumerate(lcs):
        fluxes.append(lc.flux(obsdates))

    field5 = Field.create_random(
        pointing_range=((20., 40.), (30., 40.)), radius_range=(5., 7.),
        nsources_range=(15, 25), position_error=(5./3600., 5./3600.),
        timerange=(0., 500.),
        flux_range=(1e-5, 1e-3), transients_percentage=.2)
    field6 = Field.create_random(
        pointing_range=((20., 40.), (30., 40.)), radius_range=(5., 7.),
        nsources_range=(15, 25), position_error=(5./3600., 5./3600.),
        timerange=(10., 20.),
        flux_range=(1e-5, 1e-3), transients_percentage=.2)

    figure = Figure((12, 12))
    obsdates = [obsdate for obsdate in range(5, 50)]
    #obsdates = (5., 6., 7., 10., 11., 12., 20., 30., 40., 41., 42., 43.)
    print 'observation dates =', obsdates
    observations = [Observation(obsdate=obsdate, inttime=100) for obsdate in
                    obsdates]
    axes1 = figure.add_subplot(2, 2, 1)
    axes2 = figure.add_subplot(2, 2, 3)
    fluxes = []
    detected_sources = []
    datasets = []
    images = []
    for field in [field4, field5, field6]:
        images = []
        #for source in field.sources:
        #    print source.lightcurve
        #    source.lightcurve = ChaosLC.create_random(timerange=(0., 50.))
        for observation in observations:
            images.append(Image.from_observation(
                field=field, observation=observation))
        name = "Field at %s" % field.pointing
        datasets.append(Dataset(name, images=images))
    for i, dataset in enumerate(datasets):
        fluxes = {}
        fluxerrors = {}
        for image in dataset.images:
            for j, source in enumerate(image.sources):
                fluxes.setdefault(j, []).append(source.flux.mean())
                fluxerrors.setdefault(j, []).append(image.rms)
                #fluxes[i].append(source.flux.mean())
        for j, flux_array in fluxes.items():
            axes1.errorbar(obsdates, flux_array, fluxerrors[j], fmt='-', label=('%d-%d' % (i+1, j+1)))
            axes2.errorbar(obsdates, flux_array, fluxerrors[j], fmt='-', label=('%d-%d' % (i+1, j+1)))
            #axes1.plot(obsdates, flux_array, label=('%d-%d' % (i+1, j+1)))
            #axes2.plot(obsdates, flux_array, label=('%d-%d' % (i+1, j+1)))
    axes1.set_yscale('log')
    axes1.legend(prop=FontProperties(family='sans-serif', size=6), ncol=3, labelspacing=0.01, columnspacing=0.2)
    axes2.legend(prop=FontProperties(family='sans-serif', size=6), ncol=3, labelspacing=0.01, columnspacing=0.2)
    #print '# observations =', len(observations)
    #print len(detected_sources)
    #for dataset in datasets:
    #    print dataset
    #    print "\n".join([str(image) for image in dataset.images])

    axes3 = figure.add_subplot(2, 2, 2)
    axes4 = figure.add_subplot(2, 2, 4)
    fluxes = []
    detected_sources = []
    datasets = []
    images = []
    for field in [field4, field5, field6]:
        images = []
        #for source in field.sources:
        #    source.lightcurve = ChaosLC.create_random(timerange=(0., 50.))
        for observation in observations:
            images.append(Image.from_observation(
                field=field, observation=observation, inttime=1e4))
        name = "Field at %s" % field.pointing
        datasets.append(Dataset(name, images=images))
    for i, dataset in enumerate(datasets):
        fluxes = {}
        fluxerrors = {}
        for image in dataset.images:
            for j, source in enumerate(image.sources):
                fluxes.setdefault(j, []).append(source.flux.mean())
                fluxerrors.setdefault(j, []).append(image.rms)
                #fluxes[i].append(source.flux.mean())
        for j, flux_array in fluxes.items():
            axes3.errorbar(obsdates, flux_array, fluxerrors[j], fmt='-', label=('%d-%d' % (i+1, j+1)))
            axes4.errorbar(obsdates, flux_array, fluxerrors[j], fmt='-', label=('%d-%d' % (i+1, j+1)))
    axes3.set_yscale('log')
    axes3.legend(prop=FontProperties(family='sans-serif', size=6), ncol=3, labelspacing=0.01, columnspacing=0.2)
    axes4.legend(prop=FontProperties(family='sans-serif', size=6), ncol=3, labelspacing=0.01, columnspacing=0.2)
    canvas = FigureCanvas(figure)
    canvas.print_figure('lcs.png')
    return datasets


def store_datasets(datasets, database):
    # Store in database, and find transients
    print '==== Storing datasets ===='
    T0 = datetime.datetime(2011, 1, 1)
    dataset_ids = []
    for dataset in datasets:
        print 'dataset =', dataset
        db_dataset = tkpdb.DataSet(name=dataset.name, database=database)
        print db_dataset.dsid
        dataset_ids.append(db_dataset.dsid)
        for image in dataset.images:
            #print 'image =', image
            data = {
                'taustart_ts': T0 + datetime.timedelta(image.obsdate, 0, 0),
                'tau_time': image.inttime,
                'freq_eff': 80e6,
                'freq_bw': 1e6,
                'url': ''
                }
            db_image = tkpdb.Image(dataset=db_dataset, data=data)
            results = []
            for source in image.sources:
                #flux = source.flux.mean()
                position = source.position
                #print 'position =', position, position.error_ra, position.error_dec
                results.append((position.ra, position.dec, position.error_ra,
                               position.error_dec, source.flux, image.rms,
                               source.flux, image.rms, source.flux/image.rms))
            db_image.insert_extracted_sources(results)
            db_image.associate_extracted_sources()
            print db_dataset.detect_variables()
#            db_image.associate_extracted_sources()
#            for i, transient in enumerate(db_dataset.detect_variables()):
#                transients[transient['sourceid']] = transient
#                source = tkpdb.Source(sourceid=transient['sourceid'], database=database)
#                sources[source.sourceid] = source
#                print i, transient,
#            print
    return dataset_ids

    
def get_transients(ids, database):
    # Store in database, and find transients
    print "==== Finding transient sources ===="
    sources = {}
    for dataset_id in ids:
        db_dataset = tkpdb.DataSet(dsid=dataset_id, database=database)
        print db_dataset
        #for image in db_dataset.images:
        #    print 'image =', image, type(image)
        for i, transient in enumerate(db_dataset.detect_variables()):
            source = tkpdb.Source(sourceid=transient['sourceid'], database=database)
            sources[source.sourceid] = source
    print
    print 'sources =', sources
    print
    return sources

def extract_features(sources):
    print "==== Extracting features ===="
    transients = []
    for sourceid, source in sources.iteritems():
        print '>'
        #print source.lightcurve()
        #lightcurve = sources.values()[0].lightcurve()
        lightcurve = lcmod.LightCurve(*zip(*source.lightcurve()))
        lightcurve.calc_background()
        lightcurve.calc_stats()
        lightcurve.calc_duration()
        lightcurve.calc_fluxincrease()
        lightcurve.calc_risefall()
        position = tkp.classification.manual.utils.Position(
            source.ra, source.decl, (source.ra_err, source.decl_err))
        # simplistic measure for test purposes
        variability = (lightcurve.duration['active'] /
                       lightcurve.duration['total'])
        print lightcurve.stats, lightcurve.duration['active'],
        print lightcurve.duration['total'], lightcurve.fluxincrease['peak']
        print variability
        print position
        features = {
            'duration': lightcurve.duration['total'],
            'variability': variability,
            'wmean': lightcurve.stats['wmean'],
            'median': lightcurve.stats['median'],
            'wstddev': lightcurve.stats['wstddev'],
            'wskew': lightcurve.stats['wskew'],
            'wkurtosis': lightcurve.stats['wkurtosis'],
            'max': lightcurve.stats['max'],
            'peakflux': lightcurve.fluxincrease['peak'],
            'relpeakflux': lightcurve.fluxincrease['increase']['relative'],
            'risefallratio': lightcurve.risefall['ratio'],
            }
        print features
        transients.append(tkp.classification.manual.transient.Transient(
            srcid=sourceid, position=position,
            duration=lightcurve.duration['total'], variability=variability,
            features=features))
        print transients[-1]
        print
    print
    print '----- features -----'
    print
    features = []
    for transient in transients:
        features.append([transient.features[key] for key in
                         ('wmean', 'median', 'duration', 'variability',
                          'wskew', 'wstddev', 'wkurtosis', 'relpeakflux',
                          'risefallratio')])
    print features
    print
    return 0


    args = parse_options()
    lightcurves = create(args.number, args.percentage)
    if args.plot:
        plot(lightcurves, filename='features.png',
             plot_transients=args.plot_transients,
             separate=args.plot_separate)
        
    transients = []
    ncurves = {}
    if not args.no_print:
        print "#   type            bglevel +/- sigma            max-flux         mean         stddev     skew  kurtosis      duration    activity       N"
    for lc in lightcurves:
        ncurves[lc.type] = ncurves.get(lc.type, 0) + 1
        lightcurve = lcmod.LightCurve(
            obstimes=numpy.array(
                [julian2greg(obstime) for obstime in lc.obstimes]),
            inttimes=lc.inttimes,
            fluxes=lc.fluxes,
            errors=lc.errors,
            sourceids=numpy.arange(0, len(lc.obstimes))
            )
        background = lcmod.calc_background(lightcurve)
        stats = lcmod.stats(lightcurve, -background[2])
        stats['max'] -= background[0]
        duration = lcmod.calc_duration(lightcurve, -background[2])
        if lc.type != 'constant':
            if duration[2] < 1e-7:
                lc.type = 'constant'
            else:
                transients.append([duration[2], duration[3], stats['max'], stats['mean'], stats['stddev'], stats['skew'], stats['kurtosis']])
        if not args.no_print:
            if args.print_transients:
                if lc.type == 'constant':
                    continue
            print "{:>12s}:  ".format(lc.type),
            print "{bglevel:12.4e}  {sigma:12.4e}".format(bglevel=background[0], sigma=background[1]),
            print "  {max:12.4e}  {mean:12.4e}  {stddev:12.4e}  {skew:7.4f}  {kurtosis:7.4f}".format(**stats),
            print "  {:12.4e}  {:12.4e}   {:3d}".format(duration[2]/86400., duration[3]/86400., len(numpy.where(-background[2])[0])),
            print
#        print duration[0], duration[1]
#        print "  {duration:.3f}".format(duration=duration)
#    print ncurves
    #plot(lightcurves, filename='features.png')

    # Clustering algorithms don't handle NaNs so well
    # We will have to check if this conversion works well for the clustering
    transients = numpy.nan_to_num(numpy.array(transients))
    centroids, labels = cluster(transients, args.k)
    title = "Clustering for %d transients with %d centroids" % (
        transients.shape[0], args.k)
    pdf = PdfPages('clusters.pdf')
    #pdf = 'cluster.pdf'
    plotmap(transients, axes=((1, 'active duration'), (5, 'skew')), centroids=centroids, labels=labels,
            title=title, filename=pdf)
    axes = [((1, 'active duration'), (5, 'skew')), ((1, 'active duration'), (6, 'kurtosis')),
            ((2, 'mean'), (5, 'skew')), ((0, 'duration'), (4, 'stddev'))]
    #pdf = 'clusters.pdf'
    plotmaps(transients, axes=axes, centroids=centroids, labels=labels,
            title=title, filename=pdf)
    pdf.close()
    plotmaps(transients, axes=axes, centroids=centroids, labels=labels,
            title=title, filename='kmeans2.png')

    labels, error, nfound = Pycluster.kcluster(transients, nclusters=args.k)
    centroids, cmask = Pycluster.clustercentroids(transients, clusterid=labels)
    plotmaps(transients, axes=axes, centroids=centroids, labels=labels,
             title=title, filename='pycluster.png')

    labels, centroids = milk.kmeans(transients, args.k)
    plotmap(transients, axes=((1, 'active duration'), (5, 'skew')), centroids=centroids, labels=labels,
            title=title, filename='milk1.png')
    plotmaps(transients, axes=axes, centroids=centroids, labels=labels,
            title=title, filename='milk4.png')
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
