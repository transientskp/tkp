import logging
import tkp.accessors
from tkp.accessors import sourcefinder_image_from_accessor
import tkp.accessors


logger = logging.getLogger(__name__)

def extract_sources(image_path, parset):
    """
    Extract sources from an image.

    :param image_path: path to file to extract sources from
    :param parset: parameter set *filename* containing at least the
                detection and analysis threshold and the association radius,
                the last one a multiplication factor of the de Ruiter radius.
    :returns: a list of
    """
    logger.info("Extracting image: %s" % image_path)
    accessor = tkp.accessors.open(image_path)
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
    """Force fit ?? What does this do
    Args:
        - image_path: path to image
        - positions: ?
    """
    logger.info("Forced fitting in image: %s" % (image_path))
    fitsimage = tkp.accessors.open(image_path)

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
