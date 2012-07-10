#! /usr/bin/env python

from __future__ import with_statement
from __future__ import division

"""

This script simulates light curves for the Transient database

Light curves are simulated, including their dataset and image data.
The light curves are simulated one time-step at the time, whereby for
each time-step, one or more Fields are simulated (a Field containing
various sources), imitating various LOFAR monitoring modes. This means
that groups of light curves have identical sampling, while between the
various groups, the sampling can be quite different.

Most sources will be steady sources, varying only little. A few
sources will have one or more transient episodes, and transient will
appear and disappear over the course the of the simulation (ie,
sources for which their steady-state are too faint or non-existent).

After each time-step, the transient pipeline should be run in order to:

- associate sources with previous sources or with catalogued sources

- detect transients. Only current transients should be detected.

- extract features from transient sources and run the classification


Note that no actual datasets or image data are created, just the
corresponding data in the database.


Dependencies:

  Python >= 2.5
  Database correctly set up
  External Python modules:
    argparse
    numpy, scipy, matplotlib
    tkp
    parset (local module)
    

To do (in some order of priority):

  - add a few more light curve classes

  - make light curve classes additive (or even multiplicative)
  
  - more verbose logging


List of changes:

  2010-08-11: Separate configuration file (parset)
              for fields & observations 

  2010-07-15: Allow for execution of a command after each
              insertion of all sources per image
              (eg, running the transient pipeline).

              Merged Source & TransientSource;
              a non-transient Source now has a 
              ConstantLightCurve for fluxmodel

  2010-07-14: Position errors in arcseconds
              Insert rectangular coordinates
              Insert database ids according to field

  2010-07-12: initial version

"""


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__last_modification__ = '2010-08-11'
__version__ = '0.2'


import sys
import os
from datetime import datetime, timedelta
from copy import deepcopy
import math
import subprocess
import logging
from operator import attrgetter
from argparse import ArgumentParser
import numpy
import scipy
from scipy import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib as mpl
import tkp.database.database
from parset import ParSet

#mpl.rc('text', usetex=True)



def deg2rad(degrees):
    return degrees/180.*math.pi


def greg2julian(year, month=None, day=None, hour=0, minute=0, second=0.0,
                mjd=False):
    """
    Convert a calendar date to Julian Days

    Year can be a Python datetime object

    """

    MJDOFFSET = 2400000.5
    if isinstance(year, datetime):
        yyear = year.year
        month = year.month
        day = year.day
        hour = year.hour
        minute = year.minute
        second = year.second
        year = yyear
    jd = 0.0
    if month > 12 or month < 1:
        raise ValueError, 'Month out of range'
    if day < 1 or day > 32:
        raise ValueError, 'Day out of range'
    iyear = year
    imonth = month
    iday = int (day)
    dayfrac = day - iday
    if iyear < 0:
        iyear = iyear + 1
    if month > 2:
        imonth = month + 1
    else:
        iyear = iyear - 1
	imonth = month + 13
    jd = math.floor (365.25 * iyear) + math.floor(30.6001 * imonth) + iday + 1720995
    if (iday + 31 * (month + 12 * year)) >= (15 + 31 * (10 + 12 * 1582)):
        corr = int (0.01 * iyear)
        jd = jd + 2 - corr + int (0.25 * corr)
    jd = jd + dayfrac - 0.5
    dayfrac = hour/24. + minute/1440. + second/86400.
    jd = jd + dayfrac
    if mjd:
        jd -= MJDOFFSET
    return jd


def greg2mjd(*args, **kwargs):
    return greg2julian(mjd=True, *args, **kwargs)


class LightCurve(object):
    
    def __init__(self, amplitude=0, timezero=None, **kwargs):
        self.amplitude = amplitude
        self.timezero = datetime(2001, 1, 1) if timezero is None else timezero
        super(LightCurve, self).__init__(**kwargs)

    def days(self, t):
        delta = (t - self.timezero)
        return (delta.days + delta.seconds/86400. + delta.microseconds/8.64e10)

    def __call__(self, t):
        return 0


class ConstantLightCurve(object):
    
    def __init__(self, amplitude=0, timezero=None, **kwargs):
        self.amplitude = amplitude
        self.timezero = datetime(2001, 1, 1) if timezero is None else timezero
        super(ConstantLightCurve, self).__init__(**kwargs)

    def days(self, t):
        delta = (t - self.timezero)
        return (delta.days + delta.seconds/86400. + delta.microseconds/8.64e10)

    def __call__(self, t):
        return self.amplitude


class FREDLightCurve(LightCurve):
    """Light curve with a Fast Rise, Exponential Decay"""
    
    def __init__(self, width, duration, **kwargs):
        self.width = width
        self.duration = duration
        super(FREDLightCurve, self).__init__(**kwargs)

    def __call__(self, t):
        days = self.days(t)
        return self.amplitude * ( 1 / (1 + numpy.exp(-days/self.width)) * 
                                  numpy.exp(-(days/(2*self.duration/86400))**2))

        
class GaussianLightCurve(LightCurve):
    """Light curve that rises and falls in a Gaussian bell-shaped fashion"""
    
    def __init__(self, width, **kwargs):
        self.width = width
        super(GaussianLightCurve, self).__init__(**kwargs)

    def __call__(self, t):
        days = self.days(t)
        return self.amplitude * numpy.exp(-(days/(2*self.width))**2)


class LorentzLightCurve(LightCurve):
    """Light curve that rises and falls in a Lorentzian fashion"""
    
    def __init__(self, width, **kwargs):
        self.width = width
        super(LorentzLightCurve, self).__init__(**kwargs)

    def __call__(self, t):
        days = self.days(t)
        return self.amplitude * (self.width/2)**2 / ( days**2 + self.width**2/4 )
        

class Source(object):
    """Class representing a source

    A Source instance contains a position, given by the position
    array, a position uncertainty, given by the pos_error array, and a
    flux & flux_error (both are a length 4  arrays representing
    the Stokes parameters).
    
    """
    
    def __init__(self, ra, dec, ra_error, dec_error, flux, flux_error,
                 fluxmodel=None):
        """Set base position and flux"""
        self.ra = ra
        self.dec = dec
        self.position = numpy.array([ra, dec])
        self.ra_error = ra_error
        self.dec_error = dec_error
        self.pos_error = numpy.array([ra_error, dec_error])
        self.flux = numpy.array(flux)
        self.flux_error = numpy.array(flux_error)
        self.fluxmodel = (ConstantLightCurve() if fluxmodel is None
                          else fluxmodel)

    def __str__(self):
        return "(%.1f, %.1f)  %.2g +/- %.2g" % (
            self.ra, self.dec, self.flux[0], self.flux_error[0])

    def __repr__(self):
        return "Source(%f, %f, %f, %f, %s, %s)" % (
            self.ra, self.dec, self.ra_error, self.dec_error,
            repr(self.flux), repr(self.flux_error))
    
    def setposition(self, uncertainty=0):
        """Add uncertainty to the base position"""
        self.pos_error = random.randn(2) * uncertainty
        self.position += self.pos_error
        self.pos_error = abs(self.pos_error)

    def setflux(self, midtime, noiselevel=0):
        """Simulate flux according to model, and add error"""
        self.flux += self.fluxmodel(midtime)
        self.flux += random.randn(4) * noiselevel
        self.flux_error = numpy.ones(4) * noiselevel


class FluxDistribution(object):
    """Flux distribution of constant

    Initialize with a list of two-tuples, each consisting
    of a flux level and a percentage/histogram height.
    The spread for each flux level is determined from the
    average bin size, unless width has been given in the
    initialization.

    """

    def __init__(self, fluxes, width=None):
        self.fluxes = fluxes[:]
        self._set_width(width)
        self._set_cumulative()

    def __str__(self):
        return str(self.fluxes)
    
    def _set_width(self, width):
        if width is None:
            self.width = 0
            n = len(self.fluxes)
            for i in range(1, n):
                self.width += self.fluxes[i][0] - self.fluxes[i-1][0]
            self.width /= n
        else:
            self.width = width

    def _set_cumulative(self):
        self.cumulative = [0]
        for flux in self.fluxes:
            self.cumulative.append(self.cumulative[-1]+flux[1])



class Observation(object):

    def __init__(self, field, starttime, duration, noiselevel=0,
                 uncertainty=0):
        """

        field is the Field() to be observed
        start time is a datetime object
        duration is a float, giving the integration time in seconds
        The noiselevel is somewhat arbitrary; in practice, it
            depends on duration, but also eg on station
            configuration, source elevation and weather
            (ionosphere) conditions.

        """
        self.field = field
        self.starttime = starttime   # datetime instance
        self.duration = duration     # seconds (float)
        self.noiselevel = noiselevel
        self.uncertainty = uncertainty

    def __str__(self):
        return "%s: %s + %.2f seconds" % (
            self.field.name, self.starttime.isoformat(), self.duration)
    
    def run(self):
        # print self.noiselevel, self.uncertainty
        midtime = self.starttime + timedelta(0, 0.5 * self.duration, 0)
        self.field.setfluxes(noiselevel=self.noiselevel, midtime=midtime)
        self.field.setpositions(uncertainty=self.uncertainty)
        #self.field.settransients(midtime, noiselevel=self.noiselevel)

        
class ObservingStrategy(object):

    def __init__(self, observations):
        """

        times: list of Observation() instances.

        """

        self.observations = sorted(observations, key=attrgetter('starttime'))

    def __str__(self):
        return "%s: %s" % (self.field, "; ".join(map(str, self.observations)))

    def observe(self, executable=None):
        for observation in self.observations:
            observation.run()
        return self.observations
        

class Field(object):

    def __init__(self, name, ra, dec, width, height, nsources,
                 fluxdistribution, timezero=None):
        self.name = name
        self.ra = ra
        self.dec = dec
        self.width = width
        self.height = height
        self.nsources = nsources
        self.fluxdistribution = fluxdistribution
        self.timezero = datetime.now() if timezero is None else timezero
        self.id = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Field(%s, %f, %f, %f, %f, %d, %s)" % (
            self.name, self.ra, self.dec, self.width, self.height,
            self.nsources, self.fluxdistribution)
    
    def simulate(self, fluxdistribution=None, transients=[]):
        """simulate a field of sources, each with a base flux and
        base position"""
        if len(transients) > self.nsources:
            raise ValueError("too many transients")
        if fluxdistribution is None:
            fluxdistribution = self.fluxdistribution
        ra = random.rand(self.nsources) * self.width + (
            self.ra - self.width/2.)
        dec = random.rand(self.nsources) * self.height + (
            self.dec - self.height/2.)
        flux = (random.rand(self.nsources) *
                self.fluxdistribution.cumulative[-1])
        fluxes = flux[:]
        cumulative = self.fluxdistribution.cumulative
        for i, c in enumerate(cumulative[1:]):
            fluxes[(cumulative[i] < flux) & (flux < c)] = (
                self.fluxdistribution.fluxes[i][0])
        self.sources = [Source(r, d, 0, 0, [f, 0, 0, 0], [0, 0, 0, 0]) for
                        r, d, f in zip(ra, dec, fluxes)]
        for i, transient in enumerate(transients):
            self.sources[i] = Source(
                ra[i], dec[i], 0, 0, [transient['background'], 0, 0, 0, ], 
                [0, 0, 0, 0], fluxmodel=transient['model'])

    def distroplot(self, filename):
        figure = Figure(figsize=(6, 4))
        axes1 = figure.add_subplot(1, 2, 1)
        axes1.plot([source.ra for source in self.sources],
                   [source.dec for source in self.sources], '+')
        axes2 = figure.add_subplot(1, 2, 2)
        axes2.set_xscale('log')
        axes2.hist([source.flux[0] for source in self.sources],
                   bins=(8e-9, 3e-8, 8e-8, 3e-7, 8e-7, 3e-6, 8e-6, 3e-5,
                         8e-5, 3e-4))
        canvas = FigureCanvasAgg(figure)
        canvas.print_figure(filename)
        
    def setfluxes(self, noiselevel=0, midtime=None):
        """set fluxes from base fluxes, given a noiselevel"""
        if midtime is None:
            midtime = datetime(2001, 1, 1)
        for source in self.sources:
            source.setflux(midtime, noiselevel)
            
    def setpositions(self, uncertainty=0):
        """set positions from base positions, give a positional uncertainty"""
        for source in self.sources:
            source.setposition(uncertainty=uncertainty)

        
def parse_options():
    parser = ArgumentParser(description="")
    parser.add_argument("parset", nargs='?',
                        default=os.path.splitext(sys.argv[0])[0] + ".parset",
                        help="parameter set")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s " + __version__)
    parser.add_argument("-V", "--verbose", type=int, default=3,
                        help="Level of verbose output")
    parser.add_argument("--no-database", action='store_false',
                        dest='database', default=True,
                        help="Do not save data into database")
    parser.add_argument("--figure", action='store', 
                        default="", dest='figure',
                        help="Plot light curves to <figure>")
    parser.add_argument("--running-figure", action='store',
                        default="", dest='runningfigure',
                        help="Plot new light curves every time "
                        "sources have been inserted into database")
    parser.add_argument("--distribution-plot", action='store',
                        default="", dest='distroplot',
                        help="Plot source and flux distributions")
    parser.add_argument("-C", "--command", action='store',
                        dest='command', default=None,
                        help="Execute <command> after every insertion of "
                        "all sources in a field. The image id and dataset id "
                        "are give as arguments to the command (in that order)")
    args = parser.parse_args()
    return args


def setup_logging(verbosity):
    TRACE = 5
    XINFO = 15  # extra info level
    SEVERE = 35
    logging.addLevelName(15, "OUTPUT")
    levels = [logging.CRITICAL, logging.ERROR, SEVERE,
              logging.WARNING, logging.INFO, XINFO, logging.DEBUG, TRACE]    
    loggers = {}
    handlers = {}
    formatters = {}
    handlers['main'] = logging.StreamHandler()
    formatters['main'] = logging.Formatter("%(message)s")
    handlers['main'].setFormatter(formatters['main'])
    loggers['main'] = logging.getLogger("main")
    loggers['main'].addHandler(handlers['main'])
    loggers['main'].setLevel(levels[verbosity+1])
    return loggers


def read(filename):
    with open(filename) as infile:
        for line in infile:
            lline = line.strip()
            if len(lline) == 0:
                continue
            if lline[0] in '!#%':
                continue
            cols = lline.split()


def dbase_setup():
    dbconn = tkp.database.database.connection(
        hostname="heastro1",
        database="classification",
        username="classification",
        password="classification")
    sql = dict(
        empty=["DELETE FROM basesources",
               "DELETE FROM tempbasesources",
               "DELETE FROM catalogedsources",
               "DELETE FROM catalogs",
               "DELETE FROM extractedsource",
               "DELETE FROM spectralindices",
               "DELETE FROM zoneheight",
               "DELETE FROM zones",
               "DELETE FROM images",
               "DELETE FROM frequencybands",
               "DELETE FROM datasets"],
        frequencybands="""\
INSERT INTO frequencybands
(freq_low, freq_high)
VALUES (%s, %s)
;
""",
        dataset="""\
INSERT INTO datasets
(dstype, process_ts, dsinname, dsoutname, description)
VALUES (1, %s, %s, '', '')
;
""",
        image="""\
INSERT INTO images
(dataset, tau_time, tau, taustart_ts, freq_eff, freq_bw, band, url)
VALUES (%s, %s, 1, %s, %s, %s, %s, '')
;
""",
       source="""\
INSERT INTO extractedsource
(image_id, zone, ra, decl, ra_err, decl_err, x, y, z, det_sigma,
 i_peak, i_peak_err, q_peak, q_peak_err,
 u_peak, u_peak_err, v_peak, v_peak_err, 
 i_int, i_int_err, q_int, q_int_err,
 u_int, u_int_err, v_int, v_int_err)
VALUES (%s, 0, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s)
;
""")
    return dbconn, sql


def setup(parset):
    TRANSIENT_MAPPING = dict(
        constant=ConstantLightCurve,
        gaussian=GaussianLightCurve,
        fred=FREDLightCurve,
        lorentz=LorentzLightCurve)
    
    fields = {}
    transients = {}
    epochs = {}
    durations = {}
    for field in parset['fields']:
        fluxes = field['fluxdistribution']
        fluxdistribution = FluxDistribution(
            zip(fluxes['levels'], fluxes['frequency']))
        name = field['name']
        fields[name] = Field(
            name=name, ra=field['center']['ra'], dec=field['center']['dec'],
            width=field['width'], height=field['height'],
            nsources=field['nsources'], fluxdistribution=fluxdistribution)
        transients[name] = [
            dict(background=transient['background'],
                 model=TRANSIENT_MAPPING[transient['type']](
            **transient[transient['type']]))
            for transient in field['transients']]
        epochs[name] = field['strategy']['epochs']
        durations[name] = field['strategy']['durations']

    for name, field in fields.iteritems():
        field.simulate(transients=transients[name])

    observations = []
    for name, field in fields.iteritems():
        observations.extend(
            [Observation(deepcopy(field), starttime=epoch, duration=duration,
                         noiselevel=1e-9, uncertainty=5.6e-4)
             for epoch, duration in zip(epochs[name], durations[name])])
    strategy = ObservingStrategy(observations)

    return fields, transients, strategy, observations

    
def run(options):
    logging.basicConfig(level=logging.WARNING)
    fields, transients, strategy, observations = setup(ParSet(options.parset))
    fieldnames = []
    if options.distroplot:
        base, ext = os.path.splitext(options.distroplot)
        if not ext:
            ext = '.png'
        for field in fields:
            field.distroplot("%s_%s%s" % (base, name, ext))
    for key in fields.keys():
        fieldnames.append(key)
    fieldnames = ''.join(sorted(fieldnames))
    
    if options.figure or options.runningfigure:
        data = {}
        for name in fieldnames:
            data[name] = dict(x={}, y={}, error={})
        nplots = len(fieldnames)
        nxplots = int(math.ceil(math.sqrt(nplots)))
        nyplots = nplots // nxplots
        if nxplots * nyplots < nplots:
            nyplots += 1
        
    if options.database:
        dbconn, sql = dbase_setup()
        cursor = dbconn.cursor()
        logging.info("Removing old data from database tables")
        for sql_statement in sql['empty']:
            cursor.execute(sql_statement)
            dbconn.commit()
        cursor.execute(sql['frequencybands'], (59e6, 61e6))
        dbconn.commit()
        freq_band_id = cursor.lastrowid
        # insert separate fields as separate datasets
        logging.info("Adding data fields to database")
        dataset_ids = {}
        for key in fields.keys():
            cursor.execute(sql['dataset'], (
                    datetime.now(), "Field %s" % key))
            dbconn.commit()
            dataset_ids[key] = cursor.lastrowid
        # assign datasets to each field in the observations
        for observation in observations:
            observation.field.id = dataset_ids[observation.field.name]
    for observation in strategy.observe():
        field = observation.field.name
        if options.database:
            cursor.execute(sql['image'], (
                    observation.field.id, observation.duration,
                    observation.starttime, 60e6, 2e6, freq_band_id))
            dbconn.commit()
            image_id = cursor.lastrowid
        # step through all sources in a single observation
        for i, source in enumerate(observation.field.sources):
            flux, flux_error = source.flux.tolist(), source.flux_error.tolist()
            if options.database:
                # note: convert numpy array values to intrinsic Python floats
                ra, decl = map(float, source.position)
                R = 1
                x = R * math.sin(deg2rad(decl)) * math.cos(deg2rad(ra))
                y = R * math.sin(deg2rad(decl)) * math.sin(deg2rad(ra))
                z = R * math.cos(deg2rad(decl))
                sigma = flux[0]/flux_error[0]
                cursor.execute(sql['source'], (
                    image_id, ra, decl,
                    float(3600.*source.pos_error[0]), 
                    float(3600.*source.pos_error[1]), 
                    x, y, z, sigma,
                    flux[0], flux_error[0], flux[1], flux_error[1], 
                    flux[2], flux_error[2], flux[3], flux_error[3], 
                    flux[0], flux_error[0], flux[1], flux_error[1], 
                    flux[2], flux_error[2], flux[3], flux_error[3]))
            if options.figure or options.runningfigure:
                data[field]['x'].setdefault(i, []).append(observation.starttime)
                data[field]['y'].setdefault(i, []).append(flux[0])
                data[field]['error'].setdefault(i, []).append(flux_error[0])
        if options.database:
            dbconn.commit()
            if options.command:
                args = [options.command, str(image_id), str(observation.field.id)]
                sys.stdout.write(" ".join(args) + "\n")
                cmd = subprocess.Popen(args=args, stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
                stdout, stderr = cmd.communicate()
                if cmd.returncode:
                    dbconn.close()
                    sys.stderr.write(stdout)
                    sys.stderr.write(stderr)
                    sys.stderr.write("Pipeline exited with code %d\n" %
                                     cmd.returncode)
                    raise RuntimeError(stderr)
                sys.stdout.write(stdout)
        if options.runningfigure:
            figure = Figure(figsize=(10, 10))
            axes = dict(zip(fieldnames, [figure.add_subplot(nyplots, nxplots, i)
                                         for i in range(1, nplots+1)]))
            for key, axis in axes.iteritems():
                for i in data[key]['x'].iterkeys():
                    axis.errorbar(x=map(greg2mjd, data[key]['x'][i]),
                                  y=data[key]['y'][i],
                                  yerr=data[key]['error'][i])
                axis.set_title(key)
                axis.set_yscale('log')
                axis.set_xlabel('MJD')
                axis.set_ylabel('Flux (arbitrary)')
            canvas = FigureCanvasAgg(figure)
            canvas.print_figure(options.runningfigure)
    if options.figure:
        figure = Figure(figsize=(10, 10))
        axes = dict(zip(fieldnames, [figure.add_subplot(nyplots, nxplots, i)
                                     for i in range(1, nplots+1)]))
        for key, axis in axes.iteritems():
            for i in data[key]['x'].iterkeys():
                axis.errorbar(x=map(greg2mjd, data[key]['x'][i]), y=data[key]['y'][i],
                              yerr=data[key]['error'][i])
            axis.set_title(key)
            axis.set_yscale('log')
            axis.set_xlabel('MJD')
            axis.set_ylabel('Flux (arbitrary)')
        canvas = FigureCanvasAgg(figure)
        canvas.print_figure(options.figure)
    
    return 0


def main():
    args = parse_options()
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
