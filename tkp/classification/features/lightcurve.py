"""

.. module:: lightcurve

:synopsis: Obtain light curve characteristics of a transient source

.. moduleauthor: Evert Rol, Transient Key Project <discovery@transientskp.org>

"""


from datetime import timedelta
import logging
import numpy
import pygsl.statistics
from tkp.utility.sigmaclip import calcsigma
from tkp.classification.transient import DateTime
from .sql import lightcurve as sql_lightcurve


SECONDS_IN_DAY = 86400.

class LightCurve(object):
    """
    Simple class that holds a light curve by means of several numpy
    arrays.
    """

    @classmethod
    def from_database(cursor, srcid):
        """
        Extract the complete light curve from the database

        Args:

            cursor: database cursor

            srcid (int): id of the source in the database

        Fills the attributes with data obtained from the
        database. Attributes of the class are the same as those for
        the constructor. In this case, the srcids attribute is always
        filled, and reflects the individual extracted sources.

        Example::

            >>> with closing(DataBase()) as database:
            ...     lightcurve = LightCurve.from_database(database.cursor, 1)

        """
        cursor.execute(sql_lightcurve, srcid)
        results = zip(*cursor.fetchall())
        return LightCurve(
            taustart_tss=numpy.array(results[0]),
            tau_times=numpy.array(results[1]),
            fluxes=numpy.array(results[2]),
            errors=numpy.array(results[3]),
            srcids=numpy.array(results[4])
            )

    def __init__(self, taustart_tss, tau_times, fluxes, errors, srcids=None, bands=None, stokes=None, freq_central=None):
        """
        Args:

            taustart_tss (list or array of datetime.datetime() instances):
            (mid) observing times

            tau_times (list or array of floats): integration times in seconds

            fluxes (list or array of floats): flux levels in Janskys

            errors (list or array of floats): flux errors in Janskys

            srcids (list or array of ints, None): database id of 'extracted
            source' for each data point. If left to the default of None, this
            is ignored.

            bands (list or array of ints, None): frequency band ID's

            stokes (list or array of ints, None): stokes

        Raises:

            - ValueError: when input arguments are not equal length.
        """
        self.taustart_tss = numpy.array(taustart_tss)
        self.tau_times = numpy.array(tau_times)
        self.fluxes = numpy.array(fluxes)
        self.errors = numpy.array(errors)
        if srcids is None:
            self.srcids = numpy.zeros(self.taustart_tss.shape)
        else:
            self.srcids = numpy.array(srcids)
        if not (len(self.taustart_tss) == len(self.tau_times) == len(self.fluxes) ==
                len(self.errors) == len(self.srcids)):
            raise ValueError("light curve data arrays are not of equal length")
        self.reset()

    def reset(self):
        """
        Reset all the extracted features to their default values

        The default values are generally numpy.nan or 0; using NaN
        often provides a better indication for other function or
        methods that the data does not exist.

        """
        self.background = {'mean': numpy.nan, 'sigma': numpy.nan,
                           'indices': None}
        self.duration = {'start': numpy.nan, 'end': numpy.nan,
                         'total': 0, 'active': 0}
        self.fluxincrease = {'increase': {'absolute': numpy.nan, 'relative': numpy.nan},
                             'peak': numpy.nan, 'ipeak': None}
        self.risefall = {'rise': {'time': numpy.nan, 'flux': numpy.nan},
                         'fall': {'time': numpy.nan, 'flux': numpy.nan},
                         'ratio': numpy.nan}
        self.stats = {'max': numpy.nan, 'mean': numpy.nan, 'stddev': numpy.nan,
                      'skew': numpy.nan, 'kurtosis': numpy.nan}

    def calc_background(self, niter=-50, kappa=(5, 5)):
        """
        Estimate background flux

        Kwargs:

            niter (int): number of iterations. Passed on to sigmaclip()

            kappa (2-tuple of floats): lower and upper kappa
                values. Passed on to sigmaclip()

        Returns:

            (dict): mean, sigma, indices
                where light curve is at background level (True) and where
                not (False).

        Uses sigmaclipping to estimate a background. This only works
        well when there are enough background points.

        Also estimates the first point in time where the light curve
        deviates from the background (T_zero), and the current duration
        where the light curve is above the background.

        """

        logger = logging.getLogger('tkp')
        indices = numpy.ones(self.fluxes.shape, dtype=numpy.bool)
        nniter = -niter if niter < 0 else niter
        for i in range(nniter):
            value = numpy.median(self.fluxes[indices])
            # Get the sigma from the measured flux errors, instead of
            # deriving it from the spread in values
            sigma = numpy.mean(self.errors[indices])
            # Throw away all data that are kappa*sigma above the current
            # background value
            newindices = numpy.logical_and(
                self.fluxes < value + kappa[1] * sigma, indices)
            if niter < 0:
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
            value = numpy.median(self.fluxes[indices])
            # Get the sigma from the measured flux errors, instead of
            # deriving it from the spread in values
            sigma = numpy.mean(self.errors[indices])
            # Throw away all data that are kappa*sigma above the current
            # background value
            newindices = numpy.logical_and(
                self.fluxes > value - kappa[0] * sigma, indices)
            if niter < 0:
                if (newindices == indices).all():  # no change anymore
                    break
            indices = newindices

        if len(numpy.where(indices)[0]) > 1:
            value, sigma = calcsigma(self.fluxes[indices],
                                     self.errors[indices])
            # Now that we have the proper background, recalculate the indices
            indices = (self.fluxes > value - sigma*kappa[0]) & (self.fluxes < value + sigma*kappa[1])
        self.background['mean'] = value
        self.background['sigma'] = sigma
        self.background['indices'] = indices
        return self.background


    def calc_duration(self, indices=None):
        """Calculate duration and estimate start of the transient event

        Kwargs:

            indices (numpy.ndarray): None or a numpy.ndarray of
                relevant indices; that is, the indices for points
                where the light curve duration should be calculated.

        It calculates two durations:

        - full duration, from first rise above background until last bit
          above background. This is simply the end time - start time.

        - active duration, where any intermediate returns to the
          background level are ignored. This takes only the observed bins
          and multiplies those with their respective integration
          times. Any observations outside of any transient activity do not
          contribute to this value.

        """

        start = end = numpy.nan
        duration = active = 0
        if indices is None:
            if self.background['indices'] is None:
                self.calc_background()
            indices = -self.background['indices']
        try:
            start = self.taustart_tss[indices][0]
            error = self.tau_times[indices][0]
            start = DateTime(year=start.year, month=start.month, day=start.day,
                             hour=start.hour, minute=start.minute,
                             second=start.second, error=error/2.)
            end = self.taustart_tss[indices][-1]
            error = self.tau_times[indices][-1]
            end = DateTime(year=end.year, month=end.month, day=end.day,
                           hour=end.hour, minute=end.minute,
                           second=end.second, error=error/2.)
            duration = end - start
            duration = duration.days * 86400. + duration.seconds
            if len(numpy.where(indices)[0]) == 1:
                duration = self.tau_times[indices][0]
            active = sum(self.tau_times[indices])
        except IndexError:  # only background
            start = end = numpy.nan
            duration = active = 0.
        self.duration['start'] = start
        self.duration['end'] = end
        self.duration['total'] = duration
        self.duration['active'] = active
        return self.duration


    def calc_fluxincrease(self, background=None, indices=None):
        """Get the peak flux, its increase (absolute & relative) and
        the peak index

        Kwargs:

            background (float): previously calculated background (or
                given by the user). If not given, the background is
                calculated first.

            indices (numpy.ndarray): None or a numpy.ndarray of
                relevant indices; that is, the indices for points
                where the light curve duration should be calculated.

        Returns:

            (dict): a dictionary with keys `peak` (the peak flux),
                `ipeak` (the index of the light curve for the peak
                flux), `increase` (a dictionary of flux increase
                values, the two keys indicated the `absolute` and
                `relative` flux increase).

        In case of several local maxima (multiple outbursts), only the
        peak flux and increase/decrease for the outburst in which the
        peak flux falls is calculated.

        The peak flux can be *negative* (eg, occultation transient), in
        which case increase becomes negative.

        If all indices are True, then the source is still at its
        background level, and no clear transient exists: ipeak will
        be None, increase is an empty dict and peakflux is 0.0.

        """

        if background is None:
            if self.background['indices'] is None:
                self.calc_background()
            background = self.background
        if indices is None:
            indices = background['indices']
        if indices.all():
            return self.fluxincrease
        increase = {}
        fluxes = self.fluxes
        ipeak = abs(fluxes - background['mean']).argmax()
        peakflux = fluxes[ipeak]
        increase['absolute'] = peakflux - background['mean']
        increase['relative'] = peakflux / background['mean']
        self.fluxincrease['increase'] = increase
        self.fluxincrease['peak'] = peakflux
        self.fluxincrease['ipeak'] = ipeak
        return self.fluxincrease


    def calc_risefall(self, background=None, indices=None, ipeak=None):
        """Calculate the (total) flux increase & decrease

        Kwargs:

            background (float): previously calculated background (or
                given by the user). If not given, the background is
                calculated first.

            indices (numpy.ndarray): None or a numpy.ndarray of
                relevant indices; that is, the indices for points
                where the light curve duration should be calculated.

            ipeak: the index of the light curve maximum. If not set,
            calculated by `calc_fluxincrease`.

        Returns:

            (3-tuple):

                - the first two elements are themselves two-tuples
                  that contain the flux increase or decrease (first element)
                  and the time interval (second element).

                - the third element is a number that indicates
                  the ratio between the increase and decrease.
                  The number is zero if the increase or decrease
                  could not be calculated.


        This method calculated the flux increase and decrease, as well
        as the time interval over which the flux increases or
        decreases.

        Note: when values are not available (mostly when the light
        curve hasn't yet returned to background), they will be set to
        0. This is an integer, and one could use this to see if this is
        a calculated value or a indication of a non-available value, while
        it is still compatible with (calculated) float values, in contrast
        to eg None.
        """

        if background is None:
            if self.background['indices'] is None:
                self.calc_background()
            background = self.background
        if ipeak is None:
            if self.fluxincrease['ipeak'] is None:
                self.calc_fluxincrease()
            ipeak = self.fluxincrease['ipeak']
        if indices is None:
            indices = background['indices']
        # If we don't have a clear transient, don't try and calculate nonsense
        if ipeak is None or indices.all():
            return self.risefall

        deltaflux = self.fluxes[ipeak] - background['mean']
        ibackground = numpy.where(indices)[0]

        # calculate duration of fall
        if indices[-1] == False:  # type(numpy.bool) is not bool; can't use 'is'!
            # light curve hasn't yet returned to background
            fall = {'time': 0, 'flux': deltaflux}
        else:
            # find first index when returned background for outburst around ipeak
            iback = ibackground[numpy.where(ibackground > ipeak)[0]][0]
            delta_tfall = ((self.taustart_tss[iback] +
                            timedelta(0, self.tau_times[iback] / 2., 0)) -
                           (self.taustart_tss[ipeak] +
                            timedelta(0, self.tau_times[ipeak] / 2., 0)))
            delta_tfall = delta_tfall.days * SECONDS_IN_DAY + delta_tfall.seconds
            fall = {'time': delta_tfall, 'flux': deltaflux}

        # calculate duration of rise
        if indices[0] == False:  # type(numpy.bool) is not bool; can't use 'is'!
            # light curve started above background already
            rise = {'time': 0, 'flux': deltaflux}
        else:
            # find last index before rise for outburst around ipeak
            iback = ibackground[numpy.where(ibackground<ipeak)[0]][-1]
            delta_trise = ((self.taustart_tss[ipeak] +
                            timedelta(0, self.tau_times[ipeak] / 2., 0)) -
                           (self.taustart_tss[iback] +
                            timedelta(0, self.tau_times[iback] / 2., 0)))
            delta_trise = delta_trise.days * SECONDS_IN_DAY + delta_trise.seconds
            rise = {'time': delta_trise, 'flux': deltaflux}
        if rise['time'] != 0 and fall['time'] != 0:
            # calculate rise to fall ratio
            ratio = abs((rise['flux'] / rise['time']) /
                        (fall['flux'] / fall['time']))
        else:
            ratio = numpy.nan
        self.risefall['rise'] = rise
        self.risefall['fall'] = fall
        self.risefall['ratio'] = ratio
        return self.risefall


    def calc_stats(self, indices=None):
        """Calculate some standard statistics.

        Kwargs:

            indices (numpy.ndarray of bool): specific selection of data to
                use for calculations

        Returns:

            (dict): statistics of the *full* light curve (ie, including
                background parts): mean, standard deviation, skew,
                kurtosis. All calculated values are weighted by the flux
                errors.
        """

        if indices is None:
            indices = numpy.ones(self.fluxes.shape, dtype=numpy.bool)
        # prevent calcuation on empty light curves
        elif len(indices) == 0 or indices.any() == False:
            return self.stats
        weights = 1. / self.errors[indices]**2
        try:
            self.stats['max'] = self.fluxes[indices].max()
        except ValueError:
            raise
        self.stats['wmean'] = pygsl.statistics.wmean(weights, self.fluxes[indices])
        self.stats['median'] = numpy.median(self.fluxes[indices])
        self.stats['wstddev'] = pygsl.statistics.wsd_m(
            weights, self.fluxes[indices], self.stats['wmean'])
        self.stats['wskew'] = pygsl.statistics.wskew_m_sd(
            weights, self.fluxes[indices], self.stats['wmean'], self.stats['wstddev'])
        self.stats['wkurtosis'] = pygsl.statistics.wkurtosis_m_sd(
            weights, self.fluxes[indices], self.stats['wmean'], self.stats['wstddev'])
        return self.stats
