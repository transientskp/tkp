#! /usr/bin/env python

from __future__ import division

import sys
import random
import datetime
from argparse import ArgumentParser
import numpy
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from tkp.classification.features import lightcurve as lcmod


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


class LightCurve(object):

    def __init__(self, obstimes=None, inttimes=None, noise=0.):
        """

        Kwargs:

            obstimes (list, array of float): observation times in Julian Days

            inttimes (list, array of float): integration times in seconds

        """
        
        self.obstimes = (numpy.array([]) if obstimes is None else
                         numpy.array(obstimes))
        self.inttimes = (numpy.array([]) if inttimes is None else
                         numpy.array(inttimes))
        self.fluxes = numpy.zeros(self.obstimes.shape)
        self.noise = noise
        self.errors = self.noise * numpy.ones(self.obstimes.shape)
        if self.noise > 0:
            errors = numpy.random.normal(0., self.noise,
                                         size=self.obstimes.shape)
            self.fluxes += errors
        
    def __str__(self):
        fluxes = ["%8.3f: %12g +/- %8g" % (obstime, flux, error)
                  for obstime, flux, error in
                  zip(self.obstimes, self.fluxes, self.errors)]
        return '\n'.join(fluxes)
    
    def __add__(self, other):

        # Check that the obstimes are the same
        # (don't care too much about the integration times (yet))
        if not (abs((self.obstimes - other.obstimes)/self.obstimes) <
                1e-7).all():
            raise ValueError("observation times are not equal")
        noise = (self.noise**2 + other.noise**2)**2
        lightcurve = LightCurve(obstimes=self.obstimes, inttimes=self.inttimes,
                                noise=noise)
        lightcurve.fluxes = self.fluxes + other.fluxes
        lightcurve.errors = numpy.sqrt(self.errors**2 + other.errors**2)
        return lightcurve
                                                        

class Constant(LightCurve):

    def __init__(self, *args, **kwargs):
        level = kwargs.pop('level', 0.)
        super(Constant, self).__init__(*args, **kwargs)
        self.fluxes += level * numpy.ones(self.obstimes.shape)
        self.fluxes += self.errors


class Gauss(LightCurve):

    def __init__(self, *args, **kwargs):
        center = kwargs.pop('center', 0.)
        width = kwargs.pop('width', 1.)
        peak = kwargs.pop('peak', 1.)
        super(Gauss, self).__init__(*args, **kwargs)
        self.fluxes = peak * numpy.exp(- ((self.obstimes - center)**2 / (2 * width**2)))
        self.fluxes /= numpy.sqrt(2 * numpy.pi * width**2)
        self.fluxes += self.errors


class DoubleGauss(LightCurve):

    def __init__(self, *args, **kwargs):
        center = kwargs.pop('center', 0.)
        width = kwargs.pop('width', 1.)
        peak = kwargs.pop('peak', 1.)
        super(DoubleGauss, self).__init__(*args, **kwargs)
        fluxes1 = peak[0] * numpy.exp(- ((self.obstimes - center[0])**2 / (2 * width[0]**2)))
        fluxes1 /= numpy.sqrt(2 * numpy.pi * width[0]**2)
        fluxes2 = peak[0] * numpy.exp(- ((self.obstimes - center[1])**2 / (2 * width[1]**2)))
        fluxes2 /= numpy.sqrt(2 * numpy.pi * width[1]**2)
        self.fluxes = fluxes1 + fluxes2
        self.fluxes += self.errors
        
        
class Triangle(LightCurve):

    def __init__(self, *args, **kwargs):
        start = kwargs.pop('start', 0.)
        end = kwargs.pop('end', 1.)
        mode = kwargs.pop('mode', 0.5)
        peak = kwargs.pop('peak', 1.)
        super(Triangle, self).__init__(*args, **kwargs)
        lower = (self.obstimes >= start) & (self.obstimes < mode)
        upper = (self.obstimes >= mode) & (self.obstimes <= end)
        delta = mode - start
        self.fluxes[lower] += peak * (self.obstimes[lower] - start)/delta
        delta = end - mode
        self.fluxes[upper] += peak * (end - self.obstimes[upper])/delta
        self.fluxes += self.errors


class LogTriangle(Triangle):

    def __init__(self, *args, **kwargs):
        peak = kwargs.get('peak', 1.)
        super(LogTriangle, self).__init__(*args, **kwargs)
        fluxes = 9*(self.fluxes - self.errors)/peak + 1
        self.fluxes = peak * numpy.log10(fluxes)
        

class Block(object):

    pass


class Curve(object):

    pass


class Lorentz(LightCurve):

    def __init__(self, *args, **kwargs):
        peak = kwargs.pop('peak')
        center = kwargs.pop('center')
        width = kwargs.pop('width')
        super(Lorentz, self).__init__(*args, **kwargs)
        self.fluxes = ((0.5 * width) /
                       ( (self.obstimes - center)**2 + 0.25 * width**2))
        self.fluxes *= peak / numpy.pi 
        self.fluxes += self.errors


class Fred(LightCurve):

    def __init__(self, *args, **kwargs):
        SCALE = 10.
        power = kwargs.pop('power', 1.)
        exp = kwargs.pop('exp', 1.)
        duration = kwargs.pop('duration', SCALE)
        start = kwargs.pop('start', None)
        peak = kwargs.pop('peak', 1.)
        super(Fred, self).__init__(*args, **kwargs)
        if start is None:
            start = self.obstimes[0]
        fluxes = numpy.zeros(self.obstimes.shape)
        delta = SCALE/len(self.obstimes)
        x = numpy.arange(0, SCALE, delta)
        y = x**(1.*power)
        indices = y > 1.
        y[indices] = numpy.exp(-exp * (x[indices] - x[indices][0]))
        x = x * duration / SCALE + start
        for i, xx in enumerate(x):
            index = numpy.where(self.obstimes > xx)[0][0]
            fluxes[index] = y[i]
        self.fluxes = peak * fluxes + self.errors
        
class Chaos(LightCurve):

    def __init__(self, *args, **kwargs):
        start = kwargs.pop('start', 0.)
        delta = kwargs.pop('delta', 1.)
        mindur = kwargs.pop('mindur', 1.)
        maxdur = kwargs.pop('maxdur', 1.)
        super(Chaos, self).__init__(*args, **kwargs)
        indices = (self.obstimes >= start) & (self.obstimes <= start+maxdur)
        self.fluxes -= self.errors
        fluxes = self.fluxes[indices]
        time0 = self.obstimes[indices][0]
        for i, obstime in enumerate(self.obstimes[indices]):
            change = random.uniform(0.1*delta, delta)
            if obstime < time0+mindur:  # largely increasing light curve
                if i > 0:
                    if random.random() > 0.7:
                        change = -change
            else:
                if random.random() > 0.3:
                    change = -change
            fluxes[i] = fluxes[i-1] + change
            if fluxes[i] < 0:
                fluxes[i] = 0.
        self.fluxes[indices] = fluxes
        self.fluxes += self.errors



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
    if random.random() < percentage:   # 20% transients
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
    canvas = FigureCanvas(figure)
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
    canvas.print_figure(filename)


def parse_options():
    parser = ArgumentParser(description="")
    parser.add_argument("-n", "--number", type=int, default=10,
                        help="Number of simulated light curves")
    parser.add_argument("-c", "--percentage", type=float, default=0.2,
                        help="""\
Percentage (between 0 and 1) of light curves that are transient.""")
    parser.add_argument("-p", "--plot", action='store_true',
                        help="Plot light curves")
    parser.add_argument("--plot-transients", action='store_true',
                        help="Plot only the transient light curves")
    parser.add_argument("--plot-separate", action='store_true',
                        help="Plot every light curve separately")
    args = parser.parse_args()
    return args

    
def main():
    args = parse_options()
    lightcurves = create(args.number, args.percentage)
    if args.plot:
        plot(lightcurves, filename='features.png',
             plot_transients=args.plot_transients,
             separate=args.plot_separate)
        
    ncurves = {}
    #      doublegauss:   3.9646e-04  1.0115e-06   3.2055e-03  1.6123e-03  9.7623e-04   0.6133  -0.7617 23.7288194444
    print "#   type            bglevel +/- sigma            max-flux         mean         stddev     skew  kurtosis      duration    N"
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
        print "{:>12s}:  ".format(lc.type),
        print "{bglevel:12.4e}  {sigma:12.4e}".format(bglevel=background[0], sigma=background[1]),
        print "  {max:12.4e}  {mean:12.4e}  {stddev:12.4e}  {skew:7.4f}  {kurtosis:7.4f}".format(**stats),
        print "  {:12.4e}  {:3d}".format(duration[2]/86400., len(numpy.where(-background[2])[0])),
        print
#        print duration[0], duration[1]
#        print "  {duration:.3f}".format(duration=duration)
    print ncurves
    #plot(lightcurves, filename='features.png')
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
