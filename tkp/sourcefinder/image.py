"""
Some generic utility routines for number handling and
calculating (specific) variances
"""

import logging
import itertools
import numpy
from tkp.utility import containers
from tkp.utility.memoize import Memoize
from tkp.sourcefinder import utils
from tkp.sourcefinder import stats
from tkp.sourcefinder import extract
try:
    import ndimage
except ImportError:
    from scipy import ndimage


logger = logging.getLogger(__name__)

#
# Hard-coded configuration parameters; not user settable.
#
INTERPOLATE_ORDER = 1   # Spline order for grid interpolation
MEDIAN_FILTER = 0       # If non-zero, apply a median filter of size
                        # MEDIAN_FILTER to the background and RMS grids prior
                        # to interpolating.
MF_THRESHOLD = 0        # If MEDIAN_FILTER is non-zero, only use the filtered
                        # grid when the (absolute) difference between the raw
                        # and filtered grids is larger than MF_THRESHOLD.
DEBLEND_MINCONT = 0.005 # Min. fraction of island flux in deblended subisland
STRUCTURING_ELEMENT = [[0,1,0], [1,1,1], [0,1,0]] # Island connectiivty

class ImageData(object):
    """Encapsulates an image in terms of a numpy array + meta/headerdata.

    This is your primary contact point for interaction with images: it icludes
    facilities for source extraction and measurement, etc.
    """

    def __init__(self, data, beam, wcs, margin=0, radius=0, back_size_x=32,
                 back_size_y=32, residuals=True
    ):
        """Sets up an ImageData object.

        *Args:*
          - data (2D numpy.ndarray): actual image data
          - wcs (utility.coordinates.wcs): world coordinate system
            specification
          - beam (3-tuple): beam shape specification as
            (semimajor, semiminor, theta)

        """

        # Do data, wcs and beam need deepcopy?
        # Probably not (memory overhead, in particular for data),
        # but then the user shouldn't change them outside ImageData in the
        # mean time
        self.rawdata = data   # a 2D numpy array
        self.wcs = wcs   # a utility.coordinates.wcs instance
        self.beam = beam   # tuple of (semimaj, semimin, theta)
        self.clip = {}
        self.labels = {}
        self.freq_low = 1
        self.freq_high = 1

        self.back_size_x = back_size_x
        self.back_size_y= back_size_y
        self.margin = margin
        self.radius = radius
        self.residuals = residuals


    ###########################################################################
    #                                                                         #
    # Properties and attributes.                                              #
    #                                                                         #
    # Properties are attributes managed by methods; rather than calling the   #
    # method directly, the attribute automatically invokes it. We can use     #
    # this to do cunning transparent caching ("memoizing") etc; see the       #
    # Memoize class.                                                          #
    #                                                                         #
    # clearcache() clears all the memoized data, which can get quite large.   #
    # It may be wise to call this, for example, in an exception handler       #
    # dealing with MemoryErrors.                                              #
    #                                                                         #
    ###########################################################################
    @Memoize
    def _grids(self):
        """Gridded RMS and background data for interpolating"""
        return self.__grids()
    grids = property(fget=_grids, fdel=_grids.delete)

    @Memoize
    def _backmap(self):
        """Background map"""
        if not hasattr(self, "_user_backmap"):
            return self._interpolate(self.grids['bg'])
        else:
            return self._user_backmap

    def _set_backmap(self, bgmap):
        self._user_backmap = bgmap
        del(self.backmap)
        del(self.data_bgsubbed)

    backmap = property(fget=_backmap, fdel=_backmap.delete, fset=_set_backmap)

    @Memoize
    def _get_rm(self):
        """RMS map"""
        if not hasattr(self, "_user_noisemap"):
            return self._interpolate(self.grids['rms'], roundup=True)
        else:
            return self._user_noisemap

    def _set_rm(self, noisemap):
        self._user_noisemap = noisemap
        del(self.rmsmap)

    rmsmap = property(fget=_get_rm, fdel=_get_rm.delete, fset=_set_rm)

    @Memoize
    def _get_data(self):
        """Masked image data"""
        # We will ignore all the data which is masked for the rest of the
        # sourcefinding process. We build up the mask by stacking ("or-ing
        # together") a number of different effects:
        #
        # * A margin from the edge of the image;
        # * Any data outside a given radius from the centre of the image;
        # * Data which is "obviously" bad (equal to 0 or NaN).
        mask = numpy.zeros((self.xdim, self.ydim))
        if self.margin:
            margin_mask = numpy.ones((self.xdim, self.ydim))
            margin_mask[self.margin:-self.margin, self.margin:-self.margin] = 0
            mask = numpy.logical_or(mask, margin_mask)
        if self.radius:
            radius_mask = utils.circular_mask(self.xdim, self.ydim, self.radius)
            mask = numpy.logical_or(mask, radius_mask)
        mask = numpy.logical_or(mask, numpy.isnan(self.rawdata))
        return numpy.ma.array(self.rawdata, mask=mask)
    data = property(fget=_get_data, fdel=_get_data.delete)

    @Memoize
    def _get_data_bgsubbed(self):
        """Background subtracted masked image data"""
        return self.data - self.backmap
    data_bgsubbed = property(fget=_get_data_bgsubbed,
        fdel=_get_data_bgsubbed.delete)

    @property
    def xdim(self):
        """X pixel dimension of (unmasked) data"""
        return self.rawdata.shape[0]

    @property
    def ydim(self):
        """Y pixel dimension of (unmasked) data"""
        return self.rawdata.shape[1]

    @property
    def pixmax(self):
        """Maximum pixel value (pre-background subtraction)"""
        return self.data.max()

    @property
    def pixmin(self):
        """Minimum pixel value (pre-background subtraction)"""
        return self.data.min()

    def clearcache(self):
        """Zap any calculated data stored in this object.

        Clear the background and rms maps, labels, clip, and any locally held
        data. All of these can be reconstructed from the data accessor.

        Note that this *must* be run to pick up any new settings.
        """
        self.labels.clear()
        self.clip.clear()
        del(self.backmap)
        del(self.rmsmap)
        del(self.data)
        del(self.data_bgsubbed)
        del(self.grids)
        if hasattr(self, 'residuals_from_gauss_fitting'):
            del(self.residuals_from_gauss_fitting)
        if hasattr(self, 'residuals_from_deblending'):
            del(self.residuals_from_deblending)


    ###########################################################################
    #                                                                         #
    # General purpose image handling.                                         #
    #                                                                         #
    # Routines for saving and trimming data, and calculating background/RMS   #
    # maps (in conjuntion with the properties above).                         #
    #                                                                         #
    ###########################################################################

    # Private "support" methods
    def __grids(self):
        """Calculate background and RMS grids of this image.

        These grids can be interpolated up to make maps of the original image
        dimensions: see _interpolate().

        This is called automatically when ImageData.backmap,
        ImageData.rmsmap or ImageData.fdrmap is first accessed.
        """

        # We set up a dedicated logging subchannel, as the sigmaclip loop
        # logging is very chatty:
        sigmaclip_logger = logging.getLogger(__name__+'.sigmaclip')

        # there's no point in working with the whole of the data array
        # if it's masked.
        useful_chunk = ndimage.find_objects(numpy.where(self.data.mask, 0, 1))
        assert(len(useful_chunk) == 1)
        useful_data = self.data[useful_chunk[0]]
        my_xdim, my_ydim = useful_data.shape

        rmsgrid, bggrid = [], []
        for startx in xrange(0, my_xdim, self.back_size_x):
            rmsrow, bgrow = [], []
            for starty in xrange(0, my_ydim, self.back_size_y):
                chunk = useful_data[
                    startx:startx + self.back_size_x,
                    starty:starty + self.back_size_y
                ].ravel()
                if not chunk.any():
                    rmsrow.append(False)
                    bgrow.append(False)
                    continue
                chunk, sigma, median, num_clip_its = stats.sigma_clip(
                    chunk, self.beam)
                if len(chunk) == 0 or not chunk.any():
                    rmsrow.append(False)
                    bgrow.append(False)
                else:
                    mean = numpy.mean(chunk)
                    rmsrow.append(sigma)
                    # In the case of a crowded field, the distribution will be
                    # skewed and we take the median as the background level.
                    # Otherwise, we take 2.5 * median - 1.5 * mean. This is the
                    # same as SExtractor: see discussion at
                    # <http://terapix.iap.fr/forum/showthread.php?tid=267>.
                    # (mean - median) / sigma is a quick n' dirty skewness
                    # estimator devised by Karl Pearson.
                    if numpy.fabs(mean - median) / sigma >= 0.3:
                        sigmaclip_logger.debug(
                            'bg skewed, %f clipping iterations', num_clip_its)
                        bgrow.append(median)
                    else:
                        sigmaclip_logger.debug(
                            'bg not skewed, %f clipping iterations', num_clip_its)
                        bgrow.append(2.5 * median - 1.5 * mean)

            rmsgrid.append(rmsrow)
            bggrid.append(bgrow)

        rmsgrid = numpy.ma.array(
            rmsgrid, mask=numpy.where(numpy.array(rmsgrid) == False, 1, 0))
        bggrid = numpy.ma.array(
            bggrid, mask=numpy.where(numpy.array(bggrid) == False, 1, 0))

        return {'rms': rmsgrid, 'bg': bggrid}

    def _interpolate(self, grid, roundup=False):
        """
        Interpolate a grid to produce a map of the dimensions of the image.

        Args:

            grid (numpy.ma.MaskedArray)

        Kwargs:

            roundup (bool)

        Returns:

            (numpy.ma.MaskedArray)

        Used to transform the RMS, background or FDR grids produced by
        L{_grids()} to a map we can compare with the image data.

        If roundup is true, values of the resultant map which are lower than
        the input grid are trimmed.
        """
        # there's no point in working with the whole of the data array if it's
        # masked.
        useful_chunk = ndimage.find_objects(numpy.where(self.data.mask, 0, 1))
        assert(len(useful_chunk) == 1)
        my_xdim, my_ydim = self.data[useful_chunk[0]].shape

        if MEDIAN_FILTER:
            f_grid = ndimage.median_filter(grid, MEDIAN_FILTER)
            if MF_THRESHOLD:
                grid = numpy.where(
                    numpy.fabs(f_grid - grid) > MF_THRESHOLD, f_grid, grid
                )
            else:
                grid = f_grid

        # Bicubic spline interpolation
        xratio = float(my_xdim)/self.back_size_x
        yratio = float(my_ydim)/self.back_size_y
        # First arg: starting point. Second arg: ending point. Third arg:
        # 1j * number of points. (Why is this complex? Sometimes, NumPy has an
        # utterly baffling API...)
        slicex = slice(-0.5, -0.5+xratio, 1j*my_xdim)
        slicey = slice(-0.5, -0.5+yratio, 1j*my_ydim)
        my_map = numpy.ma.MaskedArray(numpy.zeros(self.data.shape),
                                      mask = self.data.mask)
        my_map[useful_chunk[0]] = ndimage.map_coordinates(
            grid, numpy.mgrid[slicex, slicey],
            mode='nearest', order=INTERPOLATE_ORDER)

        # If the input grid was entirely masked, then the output map must
        # also be masked: there's no useful data here. We don't search for
        # sources on a masked background/RMS, so this data will be cleanly
        # skipped by the rest of the sourcefinder
        if numpy.ma.getmask(grid).all():
            my_map.mask = True
        elif roundup:
            # In some cases, the spline interpolation may produce values
            # lower than the minimum value in the map. If required, these
            # can be trimmed off. No point doing this if the map is already
            # fully masked, though.
            my_map = numpy.ma.MaskedArray(
                    data = numpy.where(
                        my_map >= numpy.min(grid), my_map, numpy.min(grid)),
                    mask = my_map.mask
            )
        return my_map

    ###########################################################################
    #                                                                         #
    # Source extraction.                                                      #
    #                                                                         #
    # Provides for both traditional (islands-above-RMS) and FDR source        #
    # extraction systems.                                                     #
    #                                                                         #
    ###########################################################################

    def extract(self, det, anl, noisemap=None, bgmap=None, labelled_data=None,
                labels=None, deblend_nthresh=0, force_beam=False):

        """
        Kick off conventional (ie, RMS island finding) source extraction.

        Kwargs:

            det (float): detection threshold, as a multiple of the RMS
                noise. At least one pixel in a source must exceed this
                for it to be regarded as significant.

            anl (float): analysis threshold, as a multiple of the RMS
                noise. All the pixels within the island that exceed
                this will be used when fitting the source.

            noisemap (numpy.ndarray):

            bgmap (numpy.ndarray):

            deblend_nthresh (int): number of subthresholds to use for
                deblending. Set to 0 to disable.

            force_beam (bool): force all extractions to have major/minor axes
                equal to the restoring beam

        Returns:
             :class:`tkp.utility.containers.ExtractionResults`
        """

        if anl > det:
            logger.warn(
                "Analysis threshold is higher than detection threshold"
            )

        # If the image data is flat we may as well crash out here with a
        # sensible error message, otherwise the RMS estimation code will
        # crash out with a confusing error later.
        if numpy.ma.max(self.data) == numpy.ma.min(self.data):
            raise RuntimeError("Bad data: Image data is flat")

        if (type(bgmap).__name__ == 'ndarray' or
            type(bgmap).__name__ == 'MaskedArray'):
            if bgmap.shape != self.backmap.shape:
                raise IndexError("Background map has wrong shape")
            else:
                self.backmap = bgmap

        if (type(noisemap).__name__ == 'ndarray' or
            type(noisemap).__name__ == 'MaskedArray'):
            if noisemap.shape != self.rmsmap.shape:
                raise IndexError("Noisemap has wrong shape")
            if noisemap.min() < 0:
                raise ValueError("RMS noise cannot be negative")
            else:
                self.rmsmap = noisemap

        if labelled_data is not None and labelled_data.shape != self.data.shape:
                raise ValueError("Labelled map is wrong shape")

        return self._pyse(
            det * self.rmsmap, anl * self.rmsmap, deblend_nthresh, force_beam,
            labelled_data=labelled_data, labels=labels
        )

    def reverse_se(self, det):
        """Run source extraction on the negative of this image.

        Obviously, there should be no sources in the negative image, so this
        tells you about the false positive rate.

        We need to clear cached data -- backgroung map, cached clips, etc --
        before & after doing this, as they'll interfere with the normal
        extraction process. If this is regularly used, we'll want to
        implement a separate cache.
        """
        self.labels.clear()
        self.clip.clear()
        self.data_bgsubbed *= -1
        results = self.extract(det=det)
        self.data_bgsubbed *= -1
        self.labels.clear()
        self.clip.clear()
        return results

    def fd_extract(self, alpha, anl=None, noisemap=None,
                   bgmap=None, deblend_nthresh=0, force_beam=False
    ):
        """False Detection Rate based source extraction.
        The FDR procedure guarantees that <FDR> < alpha.

        See `Hopkins et al., AJ, 123, 1086 (2002)
        <http://adsabs.harvard.edu/abs/2002AJ....123.1086H>`_.
        """

        # The correlation length in config.py is used not only for the
        # calculation of error bars with the Condon formulae, but also for
        # calculating the number of independent pixels.
        corlengthlong, corlengthshort = utils.calculate_correlation_lengths(
            self.beam[0], self.beam[1])

        C_n = (1.0 / numpy.arange(
            round(0.25 * numpy.pi * corlengthlong *
                  corlengthshort + 1))[1:]).sum()

        # Calculate the FDR threshold
        # Things will go terribly wrong in the line below if the interpolated
        # noise values get very close or below zero. Use INTERPOLATE_ORDER=1
        # or the roundup option.
        if (type(bgmap).__name__ == 'ndarray' or
            type(bgmap).__name__ == 'MaskedArray'):
            if bgmap.shape != self.backmap.shape:
                raise IndexError("Background map has wrong shape")
            else:
                self.backmap = bgmap
        if (type(noisemap).__name__ == 'ndarray' or
            type(noisemap).__name__ == 'MaskedArray'):
            if noisemap.shape != self.rmsmap.shape:
                raise IndexError("Noisemap has wrong shape")
            if noisemap.min()<0:
                raise ValueError("RMS noise cannot be negative")
            else:
                self.rmsmap = noisemap

        normalized_data = self.data_bgsubbed/self.rmsmap

        n1 = numpy.sqrt(2 * numpy.pi)
        prob = numpy.sort(numpy.ravel(numpy.exp(-0.5 * normalized_data**2)/n1))
        lengthprob = float(len(prob))
        compare = (alpha / C_n) * numpy.arange(lengthprob+1)[1:] / lengthprob
        # Find the last undercrossing, see, e.g., fig. 9 in Miller et al., AJ
        # 122, 3492 (2001).  Searchsorted is not used because the array is not
        # sorted.
        try:
            index = (numpy.where(prob-compare < 0.)[0]).max()
        except ValueError:
            # Everything below threshold
            return containers.ExtractionResults()

        fdr_threshold = numpy.sqrt(-2.0 * numpy.log(n1 * prob[index]))
        # Default we require that all source pixels are above the threshold,
        # not only the peak pixel.  This gives a better guarantee that indeed
        # the fraction of false positives is less than fdr_alpha in config.py.
        # See, e.g., Hopkins et al., AJ 123, 1086 (2002).
        if not anl:
            anl = fdr_threshold
        return self._pyse(fdr_threshold * self.rmsmap, anl * self.rmsmap,
                          deblend_nthresh, force_beam)

    def flux_at_pixel(self, x, y, numpix=1):
        """Return the background-subtracted flux at a certain position
        in the map"""

        # numpix is the number of pixels to look around the target.
        # e.g. numpix = 1 means a total of 9 pixels, 1 in each direction.
        return self.data_bgsubbed[y-numpix:y+numpix+1,
                                  x-numpix:x+numpix+1].max()

    @staticmethod
    def box_slice_about_pixel(x,y,box_radius):
        """
        Returns a slice centred about (x,y), of width = 2*int(box_radius) + 1
        """
        ibr = int(box_radius)
        return (slice(x - ibr, x + ibr + 1),
                slice(y - ibr, y + ibr + 1))

    def fit_to_point(self, x, y, boxsize, threshold, fixed):
        """Fit an elliptical Gaussian to a specified point on the image.

        The fit is carried on a square section of the image, of length
        *boxsize* & centred at pixel coordinates *x*, *y*. Any data
        below *threshold* * rmsmap is not used for fitting. If *fixed*
        is set to ``position``, then the pixel coordinates are fixed
        in the fit.

        Returns an instance of :class:`tkp.sourcefinder.extract.Detection`.
        """

        logger.debug("Force-fitting pixel location ({},{})".format(x,y))
        # First, check that x and y are actually valid semi-positive integers.
        # Otherwise,
        # If they are too high (positive), then indexing will fail
        # BUT, if they are negative, then we get wrap-around indexing
        # and the fit continues at the wrong position!
        if (x < 0 or x >self.xdim
            or y < 0 or y >self.ydim ):
            logger.warning("Dropping forced fit at ({},{}), "
                           "pixel position outside image".format(x,y)
            )
            return None

        # Next, check if any of the central pixels (in a 3x3 box about the
        # fitted pixel position) have been Masked
        # (e.g. if NaNs, or close to image edge) - reject if so.
        central_pixels_slice = ImageData.box_slice_about_pixel(x, y, 1)
        if self.data.mask[central_pixels_slice].any():
            logger.warning(
                "Dropping forced fit at ({},{}), "
                   "Masked pixel in central fitting region".format(x,y))
            return None

        if ((
                # Recent NumPy
                hasattr(numpy.ma.core, "MaskedConstant") and
                isinstance(self.rmsmap, numpy.ma.core.MaskedConstant)
            ) or (
                # Old NumPy
                numpy.ma.is_masked(self.rmsmap[x, y])
        )):
            logger.error("Background is masked: cannot fit")
            return None

        chunk = ImageData.box_slice_about_pixel(x, y, boxsize/2.0)
        if threshold is not None:
            # We'll mask out anything below threshold*self.rmsmap from the fit.
            labels, num = self.labels.setdefault( #Dictionary mapping threshold -> islands map
                threshold,
                ndimage.label(
                    self.clip.setdefault( #Dictionary mapping threshold -> mask
                        threshold,
                        numpy.where(
                            self.data_bgsubbed > threshold * self.rmsmap, 1, 0
                            )
                        )
                    )
                )


            mylabel = labels[x, y]
            if mylabel == 0:  # 'Background'
                raise ValueError("Fit region is below specified threshold, fit aborted.")
            mask = numpy.where(labels[chunk] == mylabel, 0, 1)
            fitme = numpy.ma.array(self.data_bgsubbed[chunk], mask=mask)
            if len(fitme.compressed()) < 1:
                raise IndexError("Fit region too close to edge or too small")
        else:
            fitme = self.data_bgsubbed[chunk]
            if fitme.size < 1:
                raise IndexError("Fit region too close to edge or too small")

        if not len(fitme.compressed()):
            logger.error("All data is masked: cannot fit")
            return None

        # set argument for fixed parameters based on input string
        if fixed == 'position':
            fixed = {'xbar': boxsize/2.0, 'ybar': boxsize/2.0}
        elif fixed == 'position+shape':
            fixed = {'xbar': boxsize/2.0, 'ybar': boxsize/2.0,
                     'semimajor': self.beam[0],
                     'semiminor': self.beam[1],
                     'theta': self.beam[2]}
        elif fixed == None:
            fixed = {}
        else:
            raise TypeError("Unkown fixed parameter")

        if threshold is not None:
            threshold_at_pixel = threshold * self.rmsmap[x, y]
        else:
            threshold_at_pixel = None

        try:
            measurement, residuals = extract.source_profile_and_errors(
                fitme,
                threshold_at_pixel,
                self.rmsmap[x, y],
                self.beam,
                fixed=fixed
            )
        except ValueError:
            # Fit failed to converge
            # Moments are not applicable when holding parameters fixed
            logger.error("Gaussian fit failed at %f, %f", x, y)
            return None

        try:
            assert(abs(measurement['xbar']) < boxsize)
            assert(abs(measurement['ybar']) < boxsize)
        except AssertionError:
            logger.warn('Fit falls outside of box.')

        measurement['xbar'] += x-boxsize/2.0
        measurement['ybar'] += y-boxsize/2.0
        measurement.sig = (fitme / self.rmsmap[chunk]).max()

        return extract.Detection(measurement, self)

    def fit_fixed_positions(self, positions, boxsize, threshold=None,
                            fixed='position+shape',
                            ids=None):
        """
        Convenience function to fit a list of sources at the given positions

        This function wraps around fit_to_point().

        Args:
            positions (list): list of (RA, Dec) tuples. Positions to be fit,
                in decimal degrees.
            boxsize: See :py:func:`fit_to_point`
            threshold: as above.
            fixed: as above.
            ids (list): A list of identifiers. If not None, then must match
                the length and order of the ``requested_fits``. Any
                successfully fit positions will be returned in a tuple
                along with the matching id. As these are simply passed back to
                calling code they can be a string, tuple or whatever.

        In particular, boxsize is in pixel coordinates as in
        fit_to_point, not in sky coordinates.

        Returns:
            list: A list of successful fits.
                If ``ids`` is None, returns a single list of
                :class:`tkp.sourcefinder.extract.Detection` s.
                Otherwise, returns a tuple of two matched lists:
                ([detections], [matching_ids]).
        """

        if ids is not None:
            assert len(ids)==len(positions)

        successful_fits = []
        successful_ids = []
        for idx, posn in enumerate(positions):
            try:
                x, y, = self.wcs.s2p((posn[0], posn[1]))
            except RuntimeError, e:
                if (str(e).startswith("wcsp2s error: 8:") or
                    str(e).startswith("wcsp2s error: 9:")):
                    logger.warning("Input coordinates (%.2f, %.2f) invalid: ",
                                    posn[0], posn[1])
                else:
                    raise
            else:
                try:
                    fit_results = self.fit_to_point(x, y,
                                                boxsize=boxsize,
                                                threshold=threshold,
                                                fixed=fixed)
                    if not fit_results:
                        # We were unable to get a good fit
                        continue
                    if ( fit_results.ra.error == float('inf') or
                          fit_results.dec.error == float('inf')):
                        logging.warning("position errors extend outside image")
                    else:
                        successful_fits.append(fit_results)
                        if ids:
                            successful_ids.append(ids[idx])

                except IndexError as e:
                    logger.warning("Input pixel coordinates (%.2f, %.2f) "
                                    "could not be fit because: " + e.message,
                                    posn[0], posn[1])
        if ids:
            return successful_fits, successful_ids
        return successful_fits

    def label_islands(self, detectionthresholdmap, analysisthresholdmap):
        """
        Return a lablled array of pixels for fitting.

        Args:

            detectionthresholdmap (numpy.ndarray):

            analysisthresholdmap (numpy.ndarray):

        Returns:

            list of valid islands (list of int)

            labelled islands (numpy.ndarray)
        """
        # If there is no usable data, we return an empty set of islands.
        if not len(self.rmsmap.compressed()):
            logging.warning("RMS map masked; sourcefinding skipped")
            return [], numpy.zeros(self.data_bgsubbed.shape, dtype=numpy.int)

        # At this point, we select all the data which is eligible for
        # sourcefitting. We are actually using three separate filters, which
        # exclude:
        #
        # 1. Anything which has been masked before we reach this point;
        # 2. Any pixels which fall below the analysis threshold at that pixel
        #    position;
        # 3. Any pixels corresponding to a position where the RMS noise is
        #    less than RMS_FILTER (default 0.001) times the median RMS across
        #    the whole image.
        #
        # The third filter attempts to exclude those regions of the image
        # which contain no usable data; for example, the parts of the image
        # falling outside the circular region produced by awimager.
        RMS_FILTER = 0.001
        clipped_data = numpy.ma.where(
            (self.data_bgsubbed > analysisthresholdmap) &
            (self.rmsmap >= (RMS_FILTER * numpy.ma.median(self.rmsmap))),
            1, 0
        ).filled(fill_value=0)
        labelled_data, num_labels = ndimage.label(clipped_data, STRUCTURING_ELEMENT)

        labels_below_det_thr, labels_above_det_thr = [], []
        if num_labels > 0:
            # Select the labels of the islands above the analysis threshold
            # that have maximum values values above the detection threshold.
            # Like above we make sure not to select anything where either
            # the data or the noise map are masked.
            # We fill these pixels in above_det_thr with -1 to make sure
            # its labels will not be in labels_above_det_thr.
            # NB data_bgsubbed, and hence above_det_thr, is a masked array;
            # filled() sets all mased values equal to -1.
            above_det_thr = (
                self.data_bgsubbed - detectionthresholdmap
            ).filled(fill_value=-1)
            # Note that we avoid label 0 (the background).
            maximum_values = ndimage.maximum(
                above_det_thr, labelled_data, numpy.arange(1, num_labels + 1)
            )

            # If there's only one island, ndimage.maximum will return a float,
            # rather than a list. The rest of this function assumes that it's
            # always a list, so we need to convert it.
            if isinstance(maximum_values, float):
                maximum_values = [maximum_values]

            # We'll filter out the insignificant islands
            for i, x in enumerate(maximum_values, 1):
                if x < 0:
                    labels_below_det_thr.append(i)
                else:
                    labels_above_det_thr.append(i)
            # Set to zero all labelled islands that are below det_thr:
            labelled_data = numpy.where(
                numpy.in1d(labelled_data.ravel(), labels_above_det_thr).reshape(labelled_data.shape),
                labelled_data, 0
            )

        return labels_above_det_thr, labelled_data


    def _pyse(
        self, detectionthresholdmap, analysisthresholdmap,
        deblend_nthresh, force_beam, labelled_data=None, labels=[]
    ):
        """
        Run Python-based source extraction on this image.

        Args:

            detectionthresholdmap (numpy.ndarray):

            analysisthresholdmap (numpy.ndarray):

            deblend_nthresh (int): number of subthresholds for deblending. 0
                disables.

            force_beam (bool): force all extractions to have major/minor axes
                equal to the restoring beam

            labelled_data (numpy.ndarray): labelled island map (output of
            numpy.ndimage.label()). Will be calculated automatically if not
            provided.

            labels (list): list of labels in the island map to use for
            fitting.

        Returns:

            (..utility.containers.ExtractionResults):

        This is described in detail in the "Source Extraction System" document
        by John Swinbank, available from TKP svn.
        """
        # Map our chunks onto a list of islands.
        island_list = []
        if labelled_data is None:
            labels, labelled_data = self.label_islands(
                detectionthresholdmap, analysisthresholdmap
            )

        # Get a bounding box for each island:
        # NB Slices ordered by label value (1...N,)
        # 'None' returned for missing label indices.
        slices = ndimage.find_objects(labelled_data)

        for label in labels:
            chunk = slices[label-1]
            analysis_threshold = (analysisthresholdmap[chunk] /
                                  self.rmsmap[chunk]).max()
            # In selected_data only the pixels with the "correct"
            # (see above) labels are retained. Other pixel values are
            # set to -(bignum).
            # In this way, disconnected pixels within (rectangular)
            # slices around islands (particularly the large ones) do
            # not affect the source measurements.
            selected_data = numpy.ma.where(
                labelled_data[chunk] == label,
                self.data_bgsubbed[chunk].data, -extract.BIGNUM
            ).filled(fill_value=-extract.BIGNUM)

            island_list.append(
                extract.Island(
                    selected_data,
                    self.rmsmap[chunk],
                    chunk,
                    analysis_threshold,
                    detectionthresholdmap[chunk],
                    self.beam,
                    deblend_nthresh,
                    DEBLEND_MINCONT,
                    STRUCTURING_ELEMENT
                )
            )

        # If required, we can save the 'left overs' from the deblending and
        # fitting processes for later analysis. This needs setting up here:
        if self.residuals:
            self.residuals_from_gauss_fitting = numpy.zeros(self.data.shape)
            self.residuals_from_deblending = numpy.zeros(self.data.shape)
            for island in island_list:
                self.residuals_from_deblending[island.chunk] += (
                    island.data.filled(fill_value=0.))

        # Deblend each of the islands to its consituent parts, if necessary
        if deblend_nthresh:
            deblended_list = map(lambda x: x.deblend(), island_list)
            #deblended_list = [x.deblend() for x in island_list]
            island_list = list(utils.flatten(deblended_list))

        # Set up the fixed fit parameters if 'force beam' is on:
        if force_beam:
            fixed = {'semimajor': self.beam[0],
                     'semiminor': self.beam[1],
                     'theta': self.beam[2]}
        else:
            fixed = None

        # Iterate over the list of islands and measure the source in each,
        # appending it to the results list.
        results = containers.ExtractionResults()
        for island in island_list:
            fit_results = island.fit(fixed=fixed)
            if fit_results:
                measurement, residual = fit_results
            else:
                # Failed to fit; drop this island and go to the next.
                continue
            try:
                det = extract.Detection(measurement, self, chunk=island.chunk)
                if (det.ra.error == float('inf') or
                        det.dec.error == float('inf')):
                    logger.warn('Bad fit from blind extraction at pixel coords:'
                                  '%f %f - measurement discarded'
                                  '(increase fitting margin?)', det.x, det.y )
                else:
                    results.append(det)
            except RuntimeError as e:
                logger.error("Island not processed; unphysical?")

            if self.residuals:
                self.residuals_from_deblending[island.chunk] -= (
                    island.data.filled(fill_value=0.))
                self.residuals_from_gauss_fitting[island.chunk] += residual


        def is_usable(det):
            # Check that both ends of each axis are usable; that is, that they
            # fall within an unmasked part of the image.
            # The axis will not likely fall exactly on a pixel number, so
            # check all the surroundings.
            def check_point(x, y):
                x = (numpy.floor(x), numpy.ceil(x))
                y = (numpy.floor(y), numpy.ceil(y))
                for position in itertools.product(x, y):
                    try:
                        if self.data.mask[position[0], position[1]]:
                            # Point falls in mask
                            return False
                    except IndexError:
                        # Point falls completely outside image
                        return False
                # Point is ok
                return True
            for point in (
                (det.start_smaj_x, det.start_smaj_y),
                (det.start_smin_x, det.start_smin_y),
                (det.end_smaj_x, det.end_smaj_y),
                (det.end_smin_x, det.end_smin_y)
            ):
                if not check_point(*point):
                    logger.debug("Unphysical source at pixel %f, %f" % (det.x.value, det.y.value))
                    return False
            return True
        # Filter will return a list; ensure we return an ExtractionResults.
        return containers.ExtractionResults(filter(is_usable, results))
