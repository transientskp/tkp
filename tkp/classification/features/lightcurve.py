"""

.. module:: lightcurve

:synopsis: Obtain light curve characteristics of a transient source
   
.. moduleauthor: Evert Rol, Transient Key Project <software@transientskp.org>

"""


from datetime import timedelta
import logging
import numpy
import pygsl.statistics
import tkp.config
from tkp.utility.sigmaclip import sigmaclip
from tkp.utility.sigmaclip import calcsigma
from tkp.utility.sigmaclip import calcmean
from tkp.classification.manual.utils import DateTime
from .sql import lightcurve as sql_lightcurve


SECONDS_IN_DAY = 86400.



class LightCurve(object):
    """Simple class that holds a light curve by means of several numpy
    arrays
    """

    def __init__(self, obstimes, inttimes, fluxes, errors, sourceids=None):
        """

        Args:

            obstimes (list or array of datetime.datetime() instances):
                (mid) observing times
                
            inttimes (list or array of floats): integration times in
                seconds

            fluxes (list or array of floats): flux levels in Janskys

            errors (list or array of floats): flux errors in Janskys

            sourceids (list or array of ints, None): database id of
                'extracted source' for each data point. If left to the
                default of None, this is ignored.

        Raises:

            ValueError: when input arguments are not equal length.
        """
        
        self.obstimes = numpy.array(obstimes)
        self.inttimes = numpy.array(inttimes)
        self.fluxes = numpy.array(fluxes)
        self.errors = numpy.array(errors)
        if sourceids is None:
            self.sourceids = numpy.zeros(self.obstimes.shape)
        else:
            self.sourceids = numpy.array(sourceids)
        if not (len(self.obstimes) == len(self.inttimes) == len(self.fluxes) ==
                len(self.errors) == len(self.sourceids)):
            raise ValueError("light curve data arrays are not of equal length")

        
def extract(cursor, sql_args):
    """Extract the complete light curve"""

    cursor.execute(sql_lightcurve, sql_args)
    results = zip(*cursor.fetchall())
    #    results = zip(*results)
    lightcurve = LightCurve(
        obstimes=numpy.array(results[0]),
        inttimes=numpy.array(results[1]),
        fluxes=numpy.array(results[2]),
        errors=numpy.array(results[3]),
        sourceids=numpy.array(results[4])
        )
    return lightcurve


def calc_background(lightcurve, niter=-50, kappa=(5, 5)):
    """Estimate background flux

    Uses sigmaclipping to estimate a background. This only works
    well when there are enough background points.

    Also estimates the first point in time where the light curve
    deviates from the background (T_zero), and the current duration
    where the light curve is above the background.

    Args:

        lightcurve (LightCurve): light curve

    Kwargs:

        niter (int): number of iterations. Passed on to sigmaclip()

        kappa (2-tuple of floats): lower and upper kappa
            values. Passed on to sigmaclip()

    Returns:

        (3-tuple: float, float, numpy.ndarray): mean, sigma, indices
            where light curve is at background level (True) and where
            not (False).
    """

    logger = logging.getLogger('tkp')
    indices = numpy.ones(lightcurve.fluxes.shape, dtype=numpy.bool)
    nniter = -niter if niter < 0 else niter
    for i in range(nniter):
        value = numpy.median(lightcurve.fluxes[indices])
        # Get the sigma from the measured flux errors, instead of
        # deriving it from the spread in values
        sigma = numpy.mean(lightcurve.errors[indices])
        # Throw away all data that are kappa*sigma above the current
        # background value
        newindices = numpy.logical_and(
            lightcurve.fluxes < value + kappa[1] * sigma, indices)
        if iter < 0:
            if (newindices == indices).all():  # no change anymore
                break
        indices = newindices

    # Now check if there are still data below the background
    # Above, we have assumed most transients rise above the
    # background, so we filter out increases in flux, not decreases
    # We do that here now
    # We can't do it at the same time as filtering the increase,
    # because that may filter too much at one
    for i in range(nniter):
        value = numpy.median(lightcurve.fluxes[indices])
        # Get the sigma from the measured flux errors, instead of
        # deriving it from the spread in values
        sigma = numpy.mean(lightcurve.errors[indices])
        # Throw away all data that are kappa*sigma above the current
        # background value
        newindices = numpy.logical_and(
            lightcurve.fluxes > value - kappa[0] * sigma, indices)
        if iter < 0:
            if (newindices == indices).all():  # no change anymore
                break
        indices = newindices
    if len(numpy.where(indices)[0]) > 1:
        value, sigma = calcsigma(lightcurve.fluxes[indices],
                                lightcurve.errors[indices])

    #var_times = (lightcurve.obstimes[-indices],
    #             lightcurve.inttimes[-indices])
    #bkg_times = (lightcurve.obstimes[indices],
    #             lightcurve.inttimes[indices])
    return value, sigma, indices


def calc_duration(lightcurve, indices=None):
    """Calculate duration and estimate start of the transient event

    It calculates two durations:

    - full duration, from first rise above background until last bit
      above background. This is simply the end time - start time.

    - active duration, where any intermediate returns to the
      background level are ignored. This takes only the observed bins
      and multiplies those with their respective integration
      times. Any observations outside of any transient activity do not
      contribute to this value.
      
    """

    start = end = duration = active = None
    if indices is None:
        value, sigma, indices = calc_background(lightcurve)
        indices = -indices
    #elif len(indices) == 0 or indices.any() == False:
    #    return numpy.nan, numpy.nan, 0, 0
    try:
        start = lightcurve.obstimes[indices][0]
        error = lightcurve.inttimes[indices][0]
        start = DateTime(year=start.year, month=start.month, day=start.day,
                         hour=start.hour, minute=start.minute,
                         second=start.second, error=error/2.)
        end = lightcurve.obstimes[indices][-1]
        error = lightcurve.inttimes[indices][-1]
        end = DateTime(year=end.year, month=end.month, day=end.day,
                       hour=end.hour, minute=end.minute,
                       second=end.second, error=error/2.)
        duration = end - start
        duration = duration.days * 86400. + duration.seconds
        if len(numpy.where(indices)[0]) == 1:
            duration = lightcurve.inttimes[indices][0]
        active = sum(lightcurve.inttimes[indices])
    except IndexError:  # only background
        start = end = numpy.nan
        duration = active = 0.
    return start, end, duration, active


def calc_fluxincrease(lightcurve, background, indices):
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

    if indices.all():
        return 0.0, {}, None
    increase = {}
    fluxes = lightcurve.fluxes
    ipeak = abs(fluxes - background['mean']).argmax()
    peakflux = fluxes[ipeak]
    increase['absolute'] = peakflux - background['mean']
    increase['percent'] = peakflux / background['mean']
    return peakflux, increase, ipeak


def calc_risefall(lightcurve, background, indices, ipeak):
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

    # If we don't have a clear transient, don't try and calculate nonsense
    if ipeak is None or indices.all():
        return {'time': 0, 'flux': 0}, {'time': 0, 'flux': 0}, 0

    fluxes = lightcurve.fluxes
    obstimes = lightcurve.obstimes
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
        delta_tfall = ((lightcurve.obstimes[iback] +
                        timedelta(0, lightcurve.inttimes[iback] / 2., 0)) -
                       (lightcurve.obstimes[ipeak] +
                        timedelta(0, lightcurve.inttimes[ipeak] / 2., 0)))
        delta_tfall = delta_tfall.days * SECONDS_IN_DAY + delta_tfall.seconds
        fall = {'time': delta_tfall, 'flux': deltaflux}

    # calculate duration of rise
    if indices[0] == False:  # type(numpy.bool) is not bool; can't use 'is'!
        # light curve started above background already
        rise = {'time': 0, 'flux': deltaflux}
    else:
        # find last index before rise for outburst around ipeak
        iback = ibackground[numpy.where(ibackground<ipeak)[0]][-1]
        delta_trise = ((lightcurve.obstimes[ipeak] +
                        timedelta(0, lightcurve.inttimes[ipeak] / 2., 0)) -
                       (lightcurve.obstimes[iback] +
                        timedelta(0, lightcurve.inttimes[iback] / 2., 0)))
        delta_trise = delta_trise.days * SECONDS_IN_DAY + delta_trise.seconds
        rise = {'time': delta_trise, 'flux': deltaflux}
    if rise['time'] != 0 and fall['time'] != 0:
        # calculate rise to fall ratio
        ratio = abs((rise['flux'] / rise['time']) /
                    (fall['flux'] / fall['time']))
    else:
        ratio = 0

    return rise, fall, ratio


def stats(lightcurve, indices=None):
    """
    Args:

        lightcurve (LightCurve): light curve

    Kwargs:

        indices (numpy.ndarray of bool): specific selection of data to
            use for calculations
        
    Returns:

        (4-tuple): statistics of the *full* light curve (ie, including
            background parts): mean, standard deviation, skew,
            kurtosis. All calculated values are weighted by the flux
            errors.
    """

    if indices is None:
        indices = numpy.ones(lightcurve.fluxes.shape, dtype=numpy.bool)
    # prevent calcuation on empty light curves
    elif len(indices) == 0 or indices.any() == False:
        return {'max': numpy.nan, 'mean': numpy.nan, 'stddev': numpy.nan,
                'skew': numpy.nan, 'kurtosis': numpy.nan}
    weights = 1. / lightcurve.errors[indices]**2
    results = {}
    try:
        results['max'] = lightcurve.fluxes[indices].max()
    except ValueError:
        print indices, lightcurve.fluxes[indices]
        raise
    results['mean'] = pygsl.statistics.wmean(weights, lightcurve.fluxes[indices])
    results['stddev'] = pygsl.statistics.wsd_m(
        weights, lightcurve.fluxes[indices], results['mean'])
    results['skew'] = pygsl.statistics.wskew_m_sd(
        weights, lightcurve.fluxes[indices], results['mean'], results['stddev'])
    results['kurtosis'] = pygsl.statistics.wkurtosis_m_sd(
        weights, lightcurve.fluxes[indices], results['mean'], results['stddev'])
    return results
