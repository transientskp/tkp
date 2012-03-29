# -*- coding: utf-8 -*-
#
# LOFAR Transients Key Project
#
# discovery@transientskp.org
#
#
# Source fitting algorithms
#

"""
Source Extraction Helpers.

These are used in conjunction with image.ImageData.
"""

import logging
import math
# DictMixin may need to be replaced using collections.MutableMapping;
# see http://docs.python.org/library/userdict.html#UserDict.DictMixin
from UserDict import DictMixin
import numpy
try:
    import ndimage
except ImportError:
    from scipy import ndimage
from deconv import deconv
from ..utility import coordinates
from ..config import config
from ..utility.uncertain import Uncertain
from .gaussian import gaussian
from . import fitting
from . import utils


CONFIG = config['source_extraction']
# If we deblend too far, we hit the recursion limit. And it's slow.
if CONFIG['deblend'] and CONFIG['deblend_nthresh'] > 300:
    logging.warn("Limiting to 300 deblending subtresholds")
    CONFIG['deblend_nthresh'] = 300

class Island(object):
    """
    The source extraction process forms islands, which it then fits.
    Each island needs to know its position in the image (ie, x, y pixel
    value at one corner), the threshold above which it is detected
    (analysis_threshold by default, but will increase if the island is
    the result of deblending), and a data array.

    The island should provide a means of deblending: splitting itself
    apart and returning multiple sub-islands, if necessary.
    """

    def __init__(self, data, rms, chunk, analysis_threshold, detection_map,
                 beam, rms_orig=None, flux_orig=None, subthrrange=None):
        mask = numpy.where(data >= rms * analysis_threshold, 0, 1)
        self.data = numpy.ma.array(data, mask=mask)
        self.rms = rms
        self.chunk = chunk
        self.analysis_threshold = analysis_threshold
        self.detection_map = detection_map
        self.beam = beam
        self.max_pos = ndimage.maximum_position(self.data.filled(fill_value=0))
        self.position = (self.chunk[0].start, self.chunk[1].start)
        if not isinstance(rms_orig, numpy.ndarray):
            self.rms_orig = self.rms
        else:
            self.rms_orig = rms_orig
        # The idea here is to retain the flux of the original, unblended
        # island. That flux is used as a criterion for deblending.
        if not isinstance(flux_orig, float):
            self.flux_orig = self.data.sum()
        else:
            self.flux_orig = flux_orig
        if isinstance(subthrrange, numpy.ndarray):
            self.subthrrange = subthrrange
        else:
            self.subthrrange = numpy.logspace(
                numpy.log(self.data.min()),
                numpy.log(self.data.max()),
                num=CONFIG['deblend_nthresh']+1, # first value == min_orig
                base=numpy.e,
                endpoint=False
            )[1:]

    def deblend(self, niter=0):
        """Return a decomposed numpy array of all the subislands.

        Iterate up through subthresholds, looking for our island
        splitting into two. If it does, start again, with two or more
        separate islands.
        """

        for level in self.subthrrange[niter:]:

            # The idea is to retain the parent island when no significant
            # subislands are found and jump to the next subthreshold
            # using niter.
            # Deblending is started at a level higher than the lowest
            # pixel value in the island.
            # Deblending at the level of the lowest pixel value will
            # likely not yield anything, because the island was formed at
            # threshold just below that.
            # So that is why we use niter+1 (>=1) instead of niter (>=0).

            if level > self.data.max():
                # level is above the highest pixel value...
                # Return the current island.
                break
            clipped_data = numpy.where(
                self.data.filled(fill_value=0) >= level, 1, 0)
            labels, number = ndimage.label((clipped_data),
                                           CONFIG['structuring_element'])
            # If we have more than one island, then we need to make subislands.
            if number > 1:
                subislands = []
                label = 0
                for chunk in ndimage.find_objects(labels):
                    label += 1
                    newdata = numpy.where(labels == label,
                                          self.data.filled(fill_value=0.0), 0)
                    # NB: In class Island(object), rms * analysis_threshold
                    # is taken as the threshold for the bottom of the island.
                    # Everything below that level is masked.
                    # For subislands, this product should be equal to level
                    # and flat, i.e., horizontal.
                    # We can achieve this by setting rms=level*ones and
                    # analysis_threshold=1.
                    island = Island(
                                 newdata[chunk],
                                 (numpy.ones(self.data[chunk].shape) * level),
                                 (
                                     slice(self.chunk[0].start + chunk[0].start,
                                        self.chunk[0].start + chunk[0].stop),
                                     slice(self.chunk[1].start + chunk[1].start,
                                        self.chunk[1].start + chunk[1].stop)
                                 ),
                                 1,
                                 self.detection_map[chunk],
                                 self.beam,
                                 self.rms_orig[chunk[0].start:chunk[0].stop, chunk[1].start:chunk[1].stop],
                                 self.flux_orig,
                                 self.subthrrange
                            )

                    subislands.append(island)
                # This line should filter out any subisland with insufficient
                # flux, in about the same way as SExtractor.
                # Sufficient means: the flux of the branch above the
                # subthreshold (=level) must exceed some user given fraction
                # of the composite object, i.e., the original island.
                subislands = filter(
                    lambda isl: (isl.data-numpy.ma.array(
                    numpy.ones(isl.data.shape)*level,
                    mask=isl.data.mask)).sum() > CONFIG['deblend_mincont'] *
                                    self.flux_orig, subislands)
                # Discard subislands below detection threshold
                subislands = filter(
                    lambda isl: (isl.data - isl.detection_map).max() >= 0,
                    subislands)
                numbersignifsub = len(subislands)
                # Proceed with the previous island, but make sure the next
                # subthreshold is higher than the present one.
                # Or we would end up in an infinite loop...
                if numbersignifsub > 1:
                    if niter+1 < CONFIG['deblend_nthresh']:
                        # Apparently, the map command always results in
                        # nested lists.
                        return list(utils.flatten(map(
                            lambda island: island.deblend(niter=niter+1),
                            subislands)))
                    else:
                        return subislands
                elif numbersignifsub == 1 and niter+1 < CONFIG['deblend_nthresh']:
                    return Island.deblend(self, niter=niter+1)
                else:
                    # In this case we have numbersignifsub == 0 or
                    # (1 and reached the highest subthreshold level).
                    # Pull out of deblending loop, return current island.
                    break
        # We've not found any subislands: just return this island.
        return self

    def threshold(self):
        """Threshold"""
        return self.noise() * self.analysis_threshold

    def noise(self):
        """Noise at maximum position"""
        return self.rms[self.max_pos]

    def sig(self):
        """Deviation"""
        return (self.data/ self.rms_orig).max()

    def fit(self):
        """Fit the position"""
        measurement, gauss_residual = source_profile_and_errors(
            self.data, self.threshold(), self.noise(), self.beam)
        measurement["xbar"] += self.position[0] + 1 # address + offset  = address but not address + address 
        measurement["ybar"] += self.position[1] + 1 # because addresses start at 0
        measurement.sig = self.sig()
        return measurement, gauss_residual


class ParamSet(DictMixin):
    """
    All the source fitting methods should go to produce a ParamSet, which
    gives all the information necessary to make a Detection.
    """

    def __init__(self):
        self.values = {
            'peak': Uncertain(),
            'flux': Uncertain(),
            'xbar': Uncertain(),
            'ybar': Uncertain(),
            'semimajor': Uncertain(),
            'semiminor': Uncertain(),
            'theta': Uncertain(),
            'semimaj_deconv': Uncertain(),
            'semimin_deconv': Uncertain(),
            'theta_deconv': Uncertain()
            }
        # This parameter gives the number of components that could not be
        # deconvolved, IERR from deconf.f.
        self.deconv_imposs = 2
        # Where have these parameters come from?
        self.moments = False
        self.gaussian = False

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, item, value):
        if item in self.values:
            if isinstance(value, Uncertain):
                self.values[item] = value
            else:
                self.values[item].value = value
        elif item[:3] == 'err' and item[3:] in  self.values:
            self.values[item[3:]].error = value
        else:
            raise AttributeError("Invalid parameter")

    def keys(self):
        """ """
        return self.values.keys()

    def calculate_errors(self, noise, beam, threshold):
        """Calculate positioanl errors

        Uses _condon_formulae() if this object is based on a Gaussian fit,
        _error_bars_from_moments() if it's based on moments.
        """

        if self.gaussian:
            return self._condon_formulae(noise, beam)
        elif self.moments:
            return self._error_bars_from_moments(noise, beam, threshold)
        else:
            return False

    def _condon_formulae(self, noise, beam):
        """Returns the errors on parameters from Gaussian fits according to
        the Condon (PASP 109, 166 (1997)) formulae.

        These formulae are not perfect, but we'll use them for the
        time being.  (See Refregier and Brown (astro-ph/9803279v1) for
        a more rigorous approach.) It also returns the corrected peak.
        The peak is corrected for the overestimate due to the local
        noise gradient.
        """

        peak = self['peak'].value
        flux = self['flux'].value
        smaj = self['semimajor'].value
        smin = self['semiminor'].value
        theta = self['theta'].value

        alpha_maj1 = CONFIG['alpha_maj1']
        alpha_min1 = CONFIG['alpha_min1']
        alpha_maj2 = CONFIG['alpha_maj2']
        alpha_min2 = CONFIG['alpha_min2']
        alpha_maj3 = CONFIG['alpha_maj3']
        alpha_min3 = CONFIG['alpha_min3']
        clean_bias = CONFIG['clean_bias']
        clean_bias_error = CONFIG['clean_bias_error']
        frac_flux_cal_error = CONFIG['frac_flux_cal_error']
        theta_B, theta_b = utils.calculate_correlation_lengths(
            beam[0], beam[1])

        rho_sq1 = ((smaj*smin/(theta_B*theta_b)) *
                   (1.+(theta_B/(2.*smaj))**2)**alpha_maj1 *
                   (1.+(theta_b/(2.*smin))**2)**alpha_min1 *
                   (peak/noise)**2)
        rho_sq2 = ((smaj*smin/(theta_B*theta_b)) *
                   (1.+(theta_B/(2.*smaj))**2)**alpha_maj2 *
                   (1.+(theta_b/(2.*smin))**2)**alpha_min2 *
                   (peak/noise)**2)
        rho_sq3 = ((smaj*smin/(theta_B*theta_b)) *
                   (1.+(theta_B/(2.*smaj))**2)**alpha_maj3 *
                   (1.+(theta_b/(2.*smin))**2)**alpha_min3 *
                   (peak/noise)**2)

        rho1 = numpy.sqrt(rho_sq1)
        rho2 = numpy.sqrt(rho_sq2)
        rho3 = numpy.sqrt(rho_sq3)

        denom1 = numpy.sqrt(2.*numpy.log(2.)) * rho1
        denom2 = numpy.sqrt(2.*numpy.log(2.)) * rho2

        # Here you get the errors parallel to the fitted semi-major and
        # semi-minor axes as taken from the NVSS paper (Condon et al. 1998,
        # AJ, 115, 1693), formula 25.
        # Those variances are twice the theoreticals, so the errors in
        # position are sqrt(2) as large as one would get from formula 21
        # of the Condon (1997) paper.
        error_par_major = 2.*smaj/denom1
        error_par_minor = 2.*smin/denom2

        # When these errors are converted to RA and Dec,
        # calibration uncertainties will have to be added,
        # like in formulae 27 of the NVSS paper.
        errorx = numpy.sqrt((error_par_major * numpy.sin(theta))**2 +
                            (error_par_minor * numpy.cos(theta))**2)
        errory = numpy.sqrt((error_par_major * numpy.cos(theta))**2 +
                            (error_par_minor * numpy.sin(theta))**2)

        # Note that we report errors in HWHM axes instead of FWHM axes
        # so the errors are half the errors of formula 29 of the NVSS paper.
        errorsmaj = numpy.sqrt(2) * smaj / rho1
        errorsmin = numpy.sqrt(2) * smin / rho2

        if smaj > smin:
            errortheta = 2.0 * (smaj*smin/(smaj**2-smin**2))/rho2
        else:
            errortheta = numpy.pi
        if errortheta > numpy.pi:
            errortheta = numpy.pi

        peak += -noise**2/peak + clean_bias

        errorpeaksq = ((frac_flux_cal_error * peak)**2 +
                       clean_bias_error**2 +
                       2. * peak**2 / rho_sq3)

        errorpeak = numpy.sqrt(errorpeaksq)

        help1 = (errorsmaj/smaj)**2
        help2 = (errorsmin/smin)**2
        help3 = theta_B * theta_b / (4. * smaj * smin)
        errorflux = flux*numpy.sqrt(errorpeaksq/peak**2+help3*(help1+help2))

        self['peak'] = Uncertain(peak, errorpeak)
        self['flux'].error = errorflux
        self['xbar'].error = errorx
        self['ybar'].error = errory
        self['semimajor'].error = errorsmaj
        self['semiminor'].error = errorsmin
        self['theta'].error = errortheta

        return self

    def _error_bars_from_moments(self, noise, beam, threshold):
        """Provide reasonable error estimates from the moments"""

        # The formulae below should give some reasonable estimate of the
        # errors from moments, should always be higher than the errors from
        # Gauss fitting.
        peak = self['peak'].value
        flux = self['flux'].value
        smaj = self['semimajor'].value
        smin = self['semiminor'].value
        theta = self['theta'].value

        ##not used
        ##clean_bias = CONFIG['clean_bias']
        clean_bias_error = CONFIG['clean_bias_error']
        frac_flux_cal_error = CONFIG['frac_flux_cal_error']
        theta_B, theta_b = utils.calculate_correlation_lengths(
            beam[0], beam[1])

        # This formula was derived in Spreeuw's Ph.D. thesis.
        rho_sq = ((16. * smaj * smin /
                  (numpy.log(2.) * theta_B * theta_b*noise**2))
                  * ((peak - threshold) /
                     (numpy.log(peak) - numpy.log(threshold)))**2)

        rho = numpy.sqrt(rho_sq)
        denom = numpy.sqrt(2.*numpy.log(2.))*rho

        # Again, like above for the Condon formulae, we set the
        # positional variances to twice the theoretical values.
        error_par_major = 2. * smaj / denom
        error_par_minor = 2. * smin / denom

        # When these errors are converted to RA and Dec,
        # calibration uncertainties will have to be added,
        # like in formulae 27 of the NVSS paper.
        errorx = numpy.sqrt((error_par_major * numpy.sin(theta))**2
                            + (error_par_minor * numpy.cos(theta))**2)
        errory = numpy.sqrt((error_par_major * numpy.cos(theta))**2
                            + (error_par_minor * numpy.sin(theta))**2)

        # Note that we report errors in HWHM axes instead of FWHM axes
        # so the errors are half the errors of formula 29 of the NVSS paper.
        errorsmaj = numpy.sqrt(2) * smaj / rho
        errorsmin = numpy.sqrt(2) * smin / rho

        if smaj > smin:
            errortheta = 2.0 * (smaj * smin / (smaj**2 -smin**2)) / rho
        else:
            errortheta = numpy.pi
        if errortheta > numpy.pi:
            errortheta = numpy.pi

        # The peak from "moments" is just the value of the maximum pixel
        # times a correction, fudge_max_pix, for the fact that the
        # centre of the Gaussian is not at the centre of the pixel.
        # This correction is performed in fitting.py. The maximum pixel
        # method introduces a peak dependent error corresponding to the last
        # term in the expression below for errorpeaksq.
        # To this, we add, in quadrature, the errors corresponding
        # to the first and last term of the rhs of equation 37 of the
        # NVSS paper. The middle term in that equation 37 is heuristically
        # replaced by noise**2 since the threshold should not affect
        # the error from the (corrected) maximum pixel method,
        # while it is part of the expression for rho_sq above.
        errorpeaksq = ((frac_flux_cal_error*peak)**2 +
                       clean_bias_error**2+noise**2 +
                       utils.maximum_pixel_method_variance(
            beam[0], beam[1], beam[2])*peak**2)
        errorpeak = numpy.sqrt(errorpeaksq)

        help1 = (errorsmaj/smaj)**2
        help2 = (errorsmin/smin)**2
        help3 = theta_B*theta_b/(4.*smaj*smin)
        errorflux = flux*numpy.sqrt(errorpeaksq/peak**2+help3*(help1+help2))

        self['peak'].error = errorpeak
        self['flux'].error = errorflux
        self['xbar'].error = errorx
        self['ybar'].error = errory
        self['semimajor'].error = errorsmaj
        self['semiminor'].error = errorsmin
        self['theta'].error = errortheta

        return self

    def deconvolve_from_clean_beam(self, beam):
        """Deconvolve with the clean beam"""
        
        # If the fitted axes are smaller than the clean beam
        # (=restoring beam) axes, the axes and position angle
        # can be deconvolved from it.
        fmaj = 2.*self['semimajor'].value
        fmajerror = 2.*self['semimajor'].error
        fmin = 2.*self['semiminor'].value
        fminerror = 2.*self['semiminor'].error
        fpa = numpy.degrees(self['theta'].value)
        fpaerror = numpy.degrees(self['theta'].error)
        cmaj = 2.*beam[0]
        cmin = 2.*beam[1]
        cpa = numpy.degrees(beam[2])

        rmaj, rmin, rpa, ierr = deconv(fmaj, fmin, fpa, cmaj, cmin, cpa)
        # This parameter gives the number of components that could not be
        # deconvolved, IERR from deconf.f.
        self.deconv_imposs = ierr
        # Now, figure out the error bars.
        if rmaj > 0:
            # In this case the deconvolved position angle is defined.
            # For convenience we reset rpa to the interval [-90, 90].
            if rpa > 90:
                rpa = -numpy.mod(-rpa, 180.)
            self['theta_deconv'].value = rpa

            # In the general case, where the restoring beam is elliptic,
            # calculating the error bars of the deconvolved position angle
            # is more complicated than in the NVSS case, where a circular
            # restoring beam was used.
            # In the NVSS case the error bars of the deconvolved angle are
            # equal to the fitted angle.
            rmaj1, rmin1, rpa1, ierr1 = deconv(
                fmaj, fmin, fpa+fpaerror, cmaj, cmin, cpa)
            if ierr1 < 2:
                if rpa1 > 90:
                    rpa1 = -numpy.mod(-rpa1, 180.)
                rpaerror1 = numpy.abs(rpa1-rpa)
                # An angle error can never be more than 90 degrees.
                if rpaerror1 > 90.:
                    rpaerror1 = numpy.mod(-rpaerror1, 180.)
            else:
                rpaerror1 = numpy.nan
            rmaj2, rmin2, rpa2, ierr2 = deconv(
                fmaj, fmin, fpa-fpaerror, cmaj, cmin, cpa)
            if ierr2 < 2:
                if rpa2 > 90:
                    rpa2 = -numpy.mod(-rpa2, 180.)
                rpaerror2 = numpy.abs(rpa2 - rpa)
                # An angle error can never be more than 90 degrees.
                if rpaerror2 > 90.:
                    rpaerror2 = numpy.mod(-rpaerror2, 180.)
            else:
                rpaerror2 = numpy.nan
            if numpy.isnan(rpaerror1) or numpy.isnan(rpaerror2):
                self['theta_deconv'].error = numpy.nansum(
                    [rpaerror1, rpaerror2])
            else:
                self['theta_deconv'].error = numpy.mean(
                    [rpaerror1, rpaerror2])
            self['semimaj_deconv'].value = rmaj / 2.
            rmaj3, rmin3, rpa3, ierr3 = deconv(
                fmaj + fmajerror, fmin, fpa, cmaj, cmin, cpa)
            # If rmaj>0, then rmaj3 should also be > 0,
            # if I am not mistaken, see the formulas at
            # the end of ch.2 of Spreeuw's Ph.D. thesis.
            if fmaj-fmajerror > fmin:
                rmaj4, rmin4, rpa4, ierr4 = deconv(
                    fmaj-fmajerror, fmin, fpa, cmaj, cmin, cpa)
                if rmaj4 > 0:
                    self['semimaj_deconv'].error = numpy.mean(
                        [numpy.abs(rmaj3-rmaj), numpy.abs(rmaj - rmaj4)])
                else:
                    self['semimaj_deconv'].error = numpy.abs(rmaj3 - rmaj)
            else:
                rmin4, rmaj4, rpa4, ierr4 = deconv(
                    fmin, fmaj - fmajerror, fpa, cmaj, cmin, cpa)
                if rmaj4>0:
                    self['semimaj_deconv'].error = numpy.mean(
                        [numpy.abs(rmaj3-rmaj), numpy.abs(rmaj - rmaj4)])
                else:
                    self['semimaj_deconv'].error = numpy.abs(rmaj3 - rmaj)
            if rmin > 0:
                self['semimin_deconv'].value = rmin / 2.
                if fmin + fminerror < fmaj:
                    rmaj5, rmin5, rpa5, ierr5 = deconv(
                        fmaj, fmin+fminerror, fpa, cmaj, cmin, cpa)
                else:
                    rmin5, rmaj5, rpa5, ierr5 = deconv(
                        fmin+fminerror, fmaj, fpa, cmaj, cmin, cpa)
                # If rmin > 0, then rmin5 should also be > 0,
                # if I am not mistaken, see the formulas at
                # the end of ch.2 of Spreeuw's Ph.D. thesis.
                rmaj6, rmin6, rpa6, ierr6 = deconv(
                    fmaj, fmin-fminerror, fpa, cmaj, cmin, cpa)
                if rmin6 > 0:
                    self['semimin_deconv'].error = numpy.mean(
                        [numpy.abs(rmin6-rmin), numpy.abs(rmin5 - rmin)])
                else:
                    self['semimin_deconv'].error = numpy.abs(rmin5 - rmin)
            else:
                self['semimin_deconv'] = Uncertain(
                    numpy.nan, numpy.nan)
        else:
            self['semimaj_deconv'] = Uncertain(numpy.nan, numpy.nan)
            self['semimin_deconv'] = Uncertain(numpy.nan, numpy.nan)
            self['theta_deconv'] = Uncertain(numpy.nan, numpy.nan)

        return self


def source_profile_and_errors(data, threshold, noise, beam, fixed=None):
    """Return a number of measurable properties with errorbars

    Given an island of pixels it will return a number of measurable
    properties including errorbars.  It will also compute residuals
    from Gauss fitting and export these to a residual map.  And it
    will make a map of the decomposed sources.

    Args:

        data (numpy.ndarray): array of pixel values, can be a masked
            array, which is necessary for proper Gauss fitting,
            because the pixels below the threshold in the corners and
            along the edges should not be included in the fitting
            process

        threshold (float): Threshold used for selecting pixels for the
            source (ie, building an island)

        noise (float): Noise level in data

        beam (3-tuple of float): beam parameters
        
    Kwargs:

        fixed (dict): parameters to keep fixed while fitting. passed
            on to fitting.fitgaussian(): this will lock fit to only
            occur at that pixel coordinate.

    Returns:

        (tuple): a populated ParamSet, and a residual array.
    """

    if fixed is None:
        fixed = {}
    param = ParamSet()

    try:
        param.update(fitting.moments(data, beam, threshold))
        param.moments = True
    except ValueError:
        # If this happens, we have two choices:
        # 1) Bomb out and tell the user to fit something sensible instead;
        # 2) Make up our own estimate (all 1s or something) to give the
        # gaussian fitter a starting point.
        param.update({
            "peak": 1,
            "flux": 1,
            "xbar": data.shape[0]/2.0,
            "ybar": data.shape[1]/2.0,
            "semimajor": 1,
            "semiminor": 1,
            "theta": 0
            })
        logging.warn("""\
Unable to estimate gaussian parameters. Proceeding with defaults %s""",
                     str(param))

    ranges = data.nonzero()
    xmin = min(ranges[0])
    xmax = max(ranges[0])
    ymin = min(ranges[1])
    ymax = max(ranges[1])

    if (numpy.fabs(xmax-xmin) > 2) and (numpy.fabs(ymax-ymin) > 2):
        # Now we can do Gauss fitting if the island or subisland has a
        # thickness of more than 2 in both dimensions.
        try:
            param.update(fitting.fitgaussian(data, param, fixed=fixed))
            param.gaussian = True
            logging.info('Gauss fitting was successful.')
        except ValueError:
            logging.warn('Gauss fitting failed.')
    else:
        if fixed:
            # moments can't handle fixed params
            raise ValueError("fit failed with given fixed parameters")

    beamsize = utils.calculate_beamsize(beam[0], beam[1])
    param["flux"] = (numpy.pi * param["peak"] * param["semimajor"] *
                     param["semiminor"] / beamsize)
    param.calculate_errors(noise, beam, threshold)
    param.deconvolve_from_clean_beam(beam)
    if CONFIG['residuals']:
        gauss_arg = (param["peak"].value,
                     param["xbar"].value,
                     param["ybar"].value,
                     param["semimajor"].value,
                     param["semiminor"].value,
                     param["theta"].value)
        gauss_resid = -(gaussian(*gauss_arg)(
            *numpy.indices(data.shape)) - data).filled(fill_value=0.)
    else:
        gauss_resid = None

    return param, gauss_resid


class Detection(object):
    """The result of a measurement at a given position in a given image."""

    def __init__(self, paramset, imagedata, chunk=None):
        self.imagedata = imagedata
        ##self.wcs = imagedata.wcs
        self.chunk = chunk

        self.peak = paramset['peak']
        self.flux = paramset['flux']
        self.x = paramset['xbar']
        self.y = paramset['ybar']
        self.smaj = paramset['semimajor']
        self.smin = paramset['semiminor']
        self.theta = paramset['theta']
        # This parameter gives the number of components that could not
        # be deconvolved, IERR from deconf.f.
        self.dc_imposs = paramset.deconv_imposs
        self.smaj_dc = paramset['semimaj_deconv']
        self.smin_dc = paramset['semimin_deconv']
        self.theta_dc = paramset['theta_deconv']

        self.sig = paramset.sig

        try:
            self._physical_coordinates()
        except RuntimeError:
            logging.warn("Physical coordinates failed at %f, %f" % (
                self.x, self.y))
            raise

    def __getstate__(self):
        return {
            'imagedata': self.imagedata,
            'chunk': (self.chunk[0].start, self.chunk[0].stop,
                      self.chunk[1].start, self.chunk[1].stop),
            'peak': self.peak,
            'flux': self.flux,
            'x': self.x,
            'y': self.y,
            'smaj': self.smaj,
            'smin': self.smin,
            'theta': self.theta,
            'sig': self.sig
            }

    def __setstate__(self, attrdict):
        self.imagedata = attrdict['imagedata']
        self.chunk = (slice(attrdict['chunk'][0], attrdict['chunk'][1]),
                      slice(attrdict['chunk'][2], attrdict['chunk'][3]))
        self.peak = attrdict['peak']
        self.flux = attrdict['flux']
        self.x = attrdict['x']
        self.y = attrdict['y']
        self.smaj = attrdict['smaj']
        self.smin = attrdict['smin']
        self.theta = attrdict['theta']
        self.sig = attrdict['sig']

        try:
            self._physical_coordinates()
        except RuntimeError, e:
            logging.warn("Physical coordinates failed at %f, %f" % (
                self.x, self.y))
            raise

    def __getattr__(self, attrname):
        # Backwards compatibility for "errquantity" attributes
        if attrname[:3] == "err":
            return self.__getattribute__(attrname[3:]).error
        else:
            raise AttributeError(attrname)

    def __str__(self):
        return "(%.2f, %.2f) +/- (%.2f, %.2f): %.2f +/- %.2f" % (
            self.ra.value, self.dec.value, self.ra.error*360, self.dec.error*3600,
            self.peak.value, self.peak.error)

    def __repr__(self):
        return str(self)
    
    def printob(self, output=None):
        if output is None:
             output = sys.stdout;
        output.write("\nPeak =" + str(self.peak ) + " flux " +
            str(self.flux) +  "\nx = "+ str(self.x )+ "\ny = " +
            str(self.y))
        output.write("\nsmaj = "+ str(self.smaj) + "\nsmin = " +
            str(self.smin) + "\ntheta = " + str(self.theta) )
        self._physical_coordinates()
        output.write("\nRA = " + str(self.ra) + " dec = "+
            str(self.dec) + "\n")

    def printasregion(self):
        """Output to DS9 region format"""
        pi = math.pi
        return ("\nellipse(" + str(self.x.value) + "," +
            str(self.y.value) +"," + str(self.smaj.value *2) + "," +
            str(self.smin.value*2) + "," + str(self.theta.value
            -pi/2.0 ) + "r ) #color=white")
             
    def _physical_coordinates(self):
        """Convert the pixel parameters for this object into something
        physical."""

        # First, the RA & dec.
        self.ra, self.dec = [Uncertain(x) for x in self.imagedata.wcs.p2s(
            [self.x.value, self.y.value])]
        if numpy.isnan(self.dec.value) or abs(self.dec) > 90.0:
            raise ValueError("object falls outside the sky")

        # First, determine local north.
        help1 = numpy.cos(numpy.radians(self.ra.value))
        help2 = numpy.sin(numpy.radians(self.ra.value))
        help3 = numpy.cos(numpy.radians(self.dec.value))
        help4 = numpy.sin(numpy.radians(self.dec.value))
        center_position = numpy.array([help3*help1, help3*help2, help4])

        # The length of this vector is chosen such that it touches
        # the tangent plane at center position.
        # The cross product of the local north vector and the local east
        # vector will always be aligned with the center_position vector.
        local_north_position = numpy.array([0., 0., 1./center_position[2]])
        # Next, determine the orientation of the y-axis wrt local north
        # by incrementing y by a small amount and converting that
        # to celestial coordinates. That small increment is conveniently
        # chosen to be an increment of 1 pixel.

        endy_ra, endy_dec = self.imagedata.wcs.p2s(
            [self.x.value, self.y.value+1.])
        help5 = numpy.cos(numpy.radians(endy_ra))
        help6 = numpy.sin(numpy.radians(endy_ra))
        help7 = numpy.cos(numpy.radians(endy_dec))
        help8 = numpy.sin(numpy.radians(endy_dec))
        endy_position = numpy.array([help7*help5, help7*help6, help8])

        # Extend the length of endy_position to make it touch the plane
        # tangent at center_position.
        endy_position /= numpy.dot(center_position, endy_position)

        diff1 = endy_position-center_position
        diff2 = local_north_position-center_position

        cross_prod = numpy.cross(diff2, diff1)

        length_cross_sq = numpy.dot(cross_prod, cross_prod)

        normalization = numpy.dot(diff1, diff1) * numpy.dot(diff2, diff2)

        # The length of the cross product equals the product of the lengths of
        # the vectors times the sine of their angle.
        # This is the angle between the y-axis and local north,
        # measured eastwards.
        # yoffset_angle = numpy.degrees(
        #    numpy.arcsin(numpy.sqrt(length_cross_sq/normalization)))
        # The formula above is commented out because the angle computed
        # in this way will always be 0<=yoffset_angle<=90.
        # We'll use the dotproduct instead.
        yoffs_rad = (numpy.arccos(numpy.dot(diff1, diff2) /
                                  numpy.sqrt(normalization)))

        # The multiplication with -sign_cor makes sure that the angle
        # is measured eastwards (increasing RA), not westwards.
        sign_cor = (numpy.dot(cross_prod, center_position) /
                    numpy.sqrt(length_cross_sq))
        yoffs_rad *= -sign_cor
        yoffset_angle = numpy.degrees(yoffs_rad)

        # Now that we have the BPA, we can also compute the position errors
        # properly, by projecting the errors in pixel coordinates (x and y)
        # on local north and local east.
        errorx_proj = numpy.sqrt(
            (self.x.error*numpy.cos(yoffs_rad))**2 +
            (self.y.error*numpy.sin(yoffs_rad))**2)
        errory_proj = numpy.sqrt(
            (self.x.error*numpy.sin(yoffs_rad))**2 +
            (self.y.error*numpy.cos(yoffs_rad))**2)

        # Now we have to sort out which combination of errorx_proj and
        # errory_proj gives the largest errors in RA and Dec.
        end_ra1, end_dec1 = self.imagedata.wcs.p2s(
            [self.x.value+errorx_proj, self.y.value])
        end_ra2, end_dec2 = self.imagedata.wcs.p2s(
            [self.x.value, self.y.value+errory_proj])

        # Here we include the position calibration errors
        self.ra.error = CONFIG['eps_ra'] + max(
            numpy.fabs(self.ra.value - end_ra1),
            numpy.fabs(self.ra.value - end_ra2))
        self.dec.error = CONFIG['eps_dec'] + max(
            numpy.fabs(self.dec.value - end_dec1),
            numpy.fabs(self.dec.value - end_dec2))

        # Now we can compute the BPA, east from local north.
        # That these angles can simply be added is not completely trivial.
        # First, the Gaussian in gaussian.py must be such that theta is
        # measured from the positive y-axis in the direction of negative x.
        # Secondly, x and y are defined such that the direction
        # positive y-->negative x-->negative y-->positive x is the same
        # direction (counterclockwise) as (local) north-->east-->south-->west.
        # If these two conditions are matched, the formula below is valid.
        # Of course, the formula is also valid if theta is measured
        # from the positive y-axis towards positive x
        # and both of these directions are equal (clockwise).
        self.theta_celes = Uncertain(
            (numpy.degrees(self.theta.value) + yoffset_angle) % 180,
            numpy.degrees(self.theta.error))
        self.theta_dc_celes = Uncertain(
            (self.theta_dc.value + yoffset_angle) % 180,
            numpy.degrees(self.theta_dc.error))

        # Next, the axes.
        # Note that the signs of numpy.sin and numpy.cos in the
        # four expressions below are arbitrary.
        end_smaj_x = (self.x.value - numpy.sin(self.theta.value) *
                      self.smaj.value)
        end_smaj_y = (self.y.value + numpy.cos(self.theta.value) *
                      self.smaj.value)
        end_smin_x = (self.x.value + numpy.cos(self.theta.value) *
                      self.smin.value)
        end_smin_y = (self.y.value + numpy.sin(self.theta.value) *
                      self.smin.value)

        end_smaj_ra, end_smaj_dec = self.imagedata.wcs.p2s(
            [end_smaj_x, end_smaj_y])
        end_smin_ra, end_smin_dec = self.imagedata.wcs.p2s(
            [end_smin_x, end_smin_y])

        smaj_asec = coordinates.angsep(self.ra.value, self.dec.value,
                                       end_smaj_ra, end_smaj_dec)
        scaling_smaj = smaj_asec / self.smaj.value
        errsmaj_asec = scaling_smaj * self.smaj.error
        self.smaj_asec = Uncertain(smaj_asec, errsmaj_asec)

        smin_asec = coordinates.angsep(self.ra.value, self.dec.value,
                                       end_smin_ra, end_smin_dec)
        scaling_smin = smin_asec / self.smin.value
        errsmin_asec = scaling_smin * self.smin.error
        self.smin_asec = Uncertain(smin_asec, errsmin_asec)

    def distance_from(self, x, y):
        """Distance from center"""
        return ((self.x - x)**2 + (self.y - y)**2)**0.5

    def serialize_all(self):
        """Return source properties suitable for database storage.

        @rtype: tuple
        """

        # in order to let accept MonetDB the values we convert float64 to float
        # by float(self.ra.value)
        zh = 1.
        return (int(numpy.floor(self.dec.value / zh)),
                self.ra.value,
                self.dec.value,
                self.ra.error,
                self.dec.error,
                (numpy.cos(numpy.radians(self.dec.value)) *
                 numpy.cos(numpy.radians(self.ra.value))),
                (numpy.cos(numpy.radians(self.dec.value)) *
                 numpy.sin(numpy.radians(self.ra.value))),
                numpy.sin(numpy.radians(self.dec.value)),
                self.sig,
                self.peak.value,
                self.peak.error,
                self.flux.value,
                self.flux.error,
                self.smaj_asec,
                self.smin_asec,
                self.theta_celes
               )

    def serialize_all_floats(self):
        """Return source properties suitable for database storage.

        @rtype: tuple
        """

        # in order to let accept MonetDB the values we convert float64 to float
        # by float(self.ra.value)
        zh = 1.
        return (int(numpy.floor(self.dec.value / zh)),
                numpy.float(self.ra.value),
                numpy.float(self.dec.value),
                numpy.float(self.ra.error),
                numpy.float(self.dec.error),
                numpy.float(numpy.cos(numpy.radians(self.dec.value)) *
                            numpy.cos(numpy.radians(self.ra.value))),
                numpy.float(numpy.cos(numpy.radians(self.dec.value)) *
                            numpy.sin(numpy.radians(self.ra.value))),
                numpy.float(numpy.sin(numpy.radians(self.dec.value))),
                numpy.float(self.sig),
               numpy.float(self.peak.value),
                numpy.float(self.peak.error),
                numpy.float(self.flux.value),
                numpy.float(self.flux.error),
                numpy.float(self.smaj_asec),
                numpy.float(self.smin_asec),
                numpy.float(self.theta_celes)
                )

    def serialize_old(self):
        """Return source properties suitable for database storage.

        @rtype: tuple
        """

        # The database doesn't recognize numpy.float64 values, so
        # in order to let the database accept the values, we convert them
        # to float
        return (
            float(self.ra.value),
            float(self.dec.value),
            float(self.ra.error),
            float(self.dec.error),
            float(self.peak.value),
            float(self.peak.error),
            float(self.flux.value),
            float(self.flux.error),
            float(self.sig)
        )


    def serialize(self):
        """Return source properties suitable for database storage.

        @rtype: tuple
        """

        # The database doesn't recognize numpy.float64 values, so
        # in order to let the database accept the values, we convert them
        # to float
        return (
            float(self.ra.value),
            float(self.dec.value),
            float(self.ra.error),
            float(self.dec.error),
            float(self.peak.value),
            float(self.peak.error),
            float(self.flux.value),
            float(self.flux.error),
            float(self.sig),
            float(self.smaj_asec.value),
            float(self.smin_asec.value),
            float(self.theta_celes.value)
        )
