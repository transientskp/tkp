__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.2'
__last_modification__ = '2010-08-24'


from datetime import timedelta
import logging
import numpy
from tkp.utility.sigmaclip import sigmaclip, calcsigma, calcmean
from tkp.classification.manual import DateTime
from .sql import lightcurve as sql_lightcurve


SECONDS_IN_DAY = 86400.


def extract(cursor, sql_args, logger=""):
    """Extract the complete light curve"""

    logger = logging.getLogger(logger)

    cursor.execute(sql_lightcurve, sql_args)
    results = zip(*cursor.fetchall())
    #    results = zip(*results)
    lightcurve = dict(
        obstimes=numpy.array(results[0]),
        inttimes=numpy.array(results[1]),
        fluxes=numpy.array(results[2]),
        errors=numpy.array(results[3]),
        sourceid=numpy.array(results[4])
        )
    return lightcurve


def calc_background(lightcurve, logger="",
                    niter=-50, kappa=(3, 3)):
    """Estimate background flux

    Uses sigmaclipping to estimate a background. This only works
    well when there are enough background points.

    Also estimates the first point in time where the light curve
    deviates from the background (T_zero), and the current duration
    where the light curve is above the background.

    Returns three values:

    - second element is a numpy array of indices giving True where
      the light curve is at background; False where it deviates from the
      background.

    """

    # - working with log(fluxes) may be better for calculating indices.
    # - unweighted sigma clipping produces better results than weighted
    #   clipping.
    logger = logging.getLogger(logger)
    indices, niter = sigmaclip(
        lightcurve['fluxes'], errors=lightcurve['errors'], niter=-50,
        siglow=kappa[0], sighigh=kappa[1], use_median=True)
    mean, sigma = calcsigma(
        lightcurve['fluxes'][indices], lightcurve['errors'][indices])
    obstimes, inttimes = lightcurve['obstimes'], lightcurve['inttimes']
    #var_times = (lightcurve['obstimes'][-indices],
    #             lightcurve['inttimes'][-indices])
    #bkg_times = (lightcurve['obstimes'][indices],
    #             lightcurve['inttimes'][indices])
    return mean, sigma, indices


def calc_duration(obstimes, inttimes, indices, logger=""):
    """Calculate duration and estimate start of the transient event

    ``indices`` are obtained from ``calc_background``.

    """

    logger = logging.getLogger(logger)
    try:
        # get last background point before transient
        izero = numpy.where(-indices)[0][0] - 1
        if izero < 0:  # source started above background
            timestart = obstimes[0] + timedelta(0, inttimes[0] / 2., 0)
            error_ts = inttimes[0] / 2.
        else:  # T_zero between last background & first transient point
            t0 = obstimes[izero] + timedelta(0, inttimes[izero] / 2., 0)
            t1 = obstimes[izero+1] + timedelta(0, inttimes[izero+1] / 2., 0)
            dt = t1 - t0
            dt = timedelta(dt.days / 2., dt.seconds / 2.)
            timestart = t0 + dt
            error_ts = dt
            error_ts = error_ts.days * SECONDS_IN_DAY + error_ts.seconds
        # get first background point after transient
        iend = numpy.where(-indices)[0][-1] + 1
        if iend >= len(obstimes):  # source still above background
            timeend = obstimes[-1] + timedelta(0, inttimes[-1] / 2., 0)
            error_te = inttimes[-1] / 2.
        else:  # T_end between last transient and first background point
            t0 = obstimes[iend-1] + timedelta(0, inttimes[iend-1] / 2., 0)
            t1 = obstimes[iend] + timedelta(0, inttimes[iend] / 2., 0)
            dt = t1 - t0
            dt = timedelta(dt.days / 2., dt.seconds / 2.)
            timeend = t0 + dt
            error_te = dt
            error_te = error_te.days * SECONDS_IN_DAY + error_te.seconds
        duration = timeend - timestart
        timestart = DateTime(timestart.year, timestart.month, timestart.day,
                            timestart.hour, timestart.minute, timestart.second,
                            timestart.microsecond,
                            error=error_ts)
        timeend = DateTime(timeend.year, timeend.month, timeend.day,
                            timeend.hour, timeend.minute, timeend.second,
                            timeend.microsecond,
                            error=error_te)
        duration = duration.days * SECONDS_IN_DAY + duration.seconds
    except IndexError:  # all values still at background
        timestart = timeend = duration = None
    return timestart, timeend, duration


def calc_fluxincrease(lightcurve, background, indices, logger=None):
    """Get the peak flux, its increase (absolute & relative) and
    the peak index

    In case of several local maxima (multiple outbursts), only the
    peak flux and increase/decrease for the outburst in which the
    peak flux falls is calculated.

    The peak flux can be *negative* (eg, occultation transient), in
    which case increase becomes negative and decrease positive.

    If all indices are True, then the source is still at its
    background level, and no clear transient exists: ipeak will
    be None, increase is an empty dict and peakflux is 0.0.

    """

    if logger is None:
        logger = logging.getLogger()
        logging.basicConfig(level=logging.CRITICAL)
    if indices.all():
        return 0.0, {}, None
    increase = {}
    fluxes = lightcurve['fluxes']
    ipeak = abs(fluxes - background['mean']).argmax()
    peakflux = fluxes[ipeak]
    increase['absolute'] = peakflux - background['mean']
    increase['percent'] = peakflux / background['mean']
    return peakflux, increase, ipeak


def calc_risefall(lightcurve, background, indices, ipeak, logger=None):
    """Calculate the (total) flux increase & decrease

    Also calculates the time interval over which the
    flux increases or decreases.

    Returns a three tuple:

    - the first two elements are themselves two-tuples
      that contain the flux increase or decrease (first element)
      and the time interval (second element).

    - the third element is a number that indicates
      the ratio between the increase and decrease.
      The number is zero if the increase or decrease
      could not be calculated.

    Note: when values are not available (mostly when the light
    curve hasn't yet returned to background), they will be set to
    0. This is an integer, and one could use this to see if this is
    a calculated value or a indication of a non-available value, while
    it is still compatible with (calculated) float values, in contrast
    to eg None.
    """

    if logger is None:
        logger = logging.getLogger()
        logging.basicConfig(level=logging.CRITICAL)

    # If we don't have a clear transient, don't try and calculate nonsense
    if ipeak is None or indices.all():
        return {'time': 0, 'flux': 0}, {'time': 0, 'flux': 0}, 0

    fluxes = lightcurve['fluxes']
    obstimes = lightcurve['obstimes']
    #L = len(fluxes)
    #if ipeak == L-1:
    #    # Still rising, or still at background
    #    fall = rise = (0, 0)
    #    return fall, rise, 0.0

    deltaflux = fluxes[ipeak] - background['mean']
    ibackground = numpy.where(indices)[0]

    # calculate duration of fall
    if indices[-1] == False:  # type(numpy.bool) is not bool; can't use 'is'!
        # light curve hasn't yet returned to background
        fall = {'time': 0, 'flux': deltaflux}
    else:
        # find first index when returned background for outburst around ipeak
        iback = ibackground[numpy.where(ibackground > ipeak)[0]][0]
        delta_tfall = ((lightcurve['obstimes'][iback] +
                        timedelta(0, lightcurve['inttimes'][iback] / 2., 0)) -
                       (lightcurve['obstimes'][ipeak] +
                        timedelta(0, lightcurve['inttimes'][ipeak] / 2., 0)))
        delta_tfall = delta_tfall.days * SECONDS_IN_DAY + delta_tfall.seconds
        fall = {'time': delta_tfall, 'flux': deltaflux}

    # calculate duration of rise
    if indices[0] == False:  # type(numpy.bool) is not bool; can't use 'is'!
        # light curve started above background already
        rise = {'time': 0, 'flux': deltaflux}
    else:
        # find last index before rise for outburst around ipeak
        iback = ibackground[numpy.where(ibackground<ipeak)[0]][-1]
        delta_trise = ((lightcurve['obstimes'][ipeak] +
                        timedelta(0, lightcurve['inttimes'][ipeak] / 2., 0)) -
                       (lightcurve['obstimes'][iback] +
                        timedelta(0, lightcurve['inttimes'][iback] / 2., 0)))
        delta_trise = delta_trise.days * SECONDS_IN_DAY + delta_trise.seconds
        rise = {'time': delta_trise, 'flux': deltaflux}
    if rise['time'] != 0 and fall['time'] != 0:
        # calculate rise to fall ratio
        ratio = abs((rise['flux'] / rise['time']) /
                    (fall['flux'] / fall['time']))
    else:
        ratio = 0

    return rise, fall, ratio
