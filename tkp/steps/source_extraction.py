import logging
import tkp.utility.accessors
from tkp.utility.accessors import sourcefinder_image_from_accessor
import tkp.utility.accessors


logger = logging.getLogger(__name__)

def extract_sources(image_path, parset):
    """
    Extract sources from an image.

    :param image_path: path to file from which to extract sources.
    :param parset: dictionary containing at least the detection and analysis
        threshold and the association radius, the last one a multiplication
        factor of the de Ruiter radius.
    :returns: list of source measurements.
    """
    logger.info("Extracting image: %s" % image_path)
    accessor = tkp.utility.accessors.open(image_path)
    logger.debug("Detecting sources in image %s at detection threshold %s",
                 image_path, parset['detection_threshold'])
    data_image = sourcefinder_image_from_accessor(accessor,
                            margin=parset['margin'],
                            radius=parset['radius'],
                            detection_threshold=parset['detection_threshold'],
                            analysis_threshold=parset['analysis_threshold'],
                            ra_sys_err=parset['ra_sys_err'],
                            dec_sys_err=parset['dec_sys_err'],
                            force_beam=parset['force_beam'])

    logger.debug("Employing margin: %s extraction radius: %s deblend: %s deblend_nthresh: %s",
            parset['margin'],
            parset['radius'],
            parset['deblend'],
            parset['deblend_nthresh']
    )

    results = data_image.extract()  # "blind" extraction of sources
    logger.info("Detected %d sources in image %s" % (len(results), image_path))
    return [r.serialize() for r in results]


def forced_fits(image_path, positions, parset):
    """
    Perform forced source measurements on an image based on a list of
    positions.

    :param image_path: path to image for measurements.
    :param positions: list of (ra, dec) pairs for measurement.
    :param parset: configuration parameterset as a dictionary.
    """
    logger.info("Forced fitting in image: %s" % (image_path))
    fitsimage = tkp.utility.accessors.open(image_path)

    data_image = sourcefinder_image_from_accessor(fitsimage,
                            margin=parset['margin'], radius=parset['radius'],
                            detection_threshold=parset['detection_threshold'],
                            analysis_threshold=parset['analysis_threshold'],
                            ra_sys_err=parset['ra_sys_err'],
                            dec_sys_err=parset['dec_sys_err'])

    if len(positions):
        boxsize = parset['box_in_beampix'] * max(data_image.beam[0],
                                                 data_image.beam[1])
        forced_fits = data_image.fit_fixed_positions(positions, boxsize)
        return [forced_fit.serialize() for forced_fit in forced_fits]
    else:
        return []
