import logging
import tkp.accessors
from tkp.accessors import sourcefinder_image_from_accessor
import tkp.accessors


logger = logging.getLogger(__name__)

def extract_sources(image_path, extraction_params):
    """
    Extract sources from an image.

    :param image_path: path to file from which to extract sources.
    :param extraction_params: dictionary containing at least the detection and analysis
        threshold and the association radius, the last one a multiplication
        factor of the de Ruiter radius.
    :returns: list of source measurements.
    """
    logger.info("Extracting image: %s" % image_path)
    accessor = tkp.accessors.open(image_path)
    logger.debug("Detecting sources in image %s at detection threshold %s",
                 image_path, extraction_params['detection_threshold'])
    data_image = sourcefinder_image_from_accessor(accessor,
                    margin=extraction_params['margin'],
                    radius=extraction_params['extraction_radius_pix'],
                    detection_threshold=extraction_params['detection_threshold'],
                    analysis_threshold=extraction_params['analysis_threshold'],
                    ew_sys_err=extraction_params['ew_sys_err'],
                    ns_sys_err=extraction_params['ns_sys_err'],
                    force_beam=extraction_params['force_beam'])

    logger.debug("Employing margin: %s extraction radius: %s deblend: %s deblend_nthresh: %s",
            extraction_params['margin'],
            extraction_params['extraction_radius_pix'],
            extraction_params['deblend'],
            extraction_params['deblend_nthresh']
    )

    results = data_image.extract()  # "blind" extraction of sources
    logger.info("Detected %d sources in image %s" % (len(results), image_path))
    return [r.serialize() for r in results]


def forced_fits(image_path, positions, extraction_params):
    """
    Perform forced source measurements on an image based on a list of
    positions.

    :param image_path: path to image for measurements.
    :param positions: list of (ra, dec) pairs for measurement.
    :param extraction_params: source extraction parameters, as a dictionary.
    """
    logger.info("Forced fitting in image: %s" % (image_path))
    fitsimage = tkp.accessors.open(image_path)

    data_image = sourcefinder_image_from_accessor(fitsimage,
                    margin=extraction_params['margin'],
                    radius=extraction_params['extraction_radius_pix'],
                    detection_threshold=extraction_params['detection_threshold'],
                    analysis_threshold=extraction_params['analysis_threshold'],
                    ew_sys_err=extraction_params['ew_sys_err'],
                    ns_sys_err=extraction_params['ns_sys_err'])

    if len(positions):
        boxsize = extraction_params['box_in_beampix'] * max(data_image.beam[0],
                                                 data_image.beam[1])
        forced_fits = data_image.fit_fixed_positions(positions, boxsize)
        return [forced_fit.serialize() for forced_fit in forced_fits]
    else:
        return []
