import logging

from lofar.parameterset import parameterset

import tkp.utility.accessors
from tkp.utility.accessors import sourcefinder_image_from_accessor
import tkp.utility.accessors


logger = logging.getLogger(__name__)

# TODO:  FIXME! (see also 'image' unit test)
BOX_IN_BEAMPIX = 10


def parse_parset(parset_file):
    parset = parameterset(parset_file)
    return {
        'backsize_x': parset.getInt('backsize_x'),
        'backsize_y': parset.getInt('backsize_y'),
        'margin': parset.getFloat('margin'),
        'deblend': parset.getBool('deblend'),
        'deblend_nthresh': parset.getInt('deblend_nthresh'),
        'radius': parset.getFloat('radius'),
        'ra_sys_err': parset.getFloat('ra_sys_err'),
        'dec_sys_err': parset.getFloat('dec_sys_err'),
        'detection_threshold': parset.getFloat('detection_threshold'),
        'analysis_threshold': parset.getFloat('analysis_threshold'),
    }


def extract_sources(image_path, parset_file):
    """Extract sources from an image
    Args:
        - image_path: path to file to extract sources from
        - parset: parameter set *filename* containing at least the
                detection and analysis threshold and the association radius,
                the last one a multiplication factor of the de Ruiter radius.
    """
    logger.info("Extracting image: %s" % (image_path))
    fitsimage = tkp.utility.accessors.open(image_path)
    parset = parse_parset(parset_file)

    logger.debug("Detecting sources in image %s at detection threshold %s",
                                    image_path, parset['detection_threshold'])

    data_image = sourcefinder_image_from_accessor(fitsimage,
                            margin=parset['margin'], radius=parset['radius'],
                            detection_threshold=parset['detection_threshold'],
                            analysis_threshold=parset['analysis_threshold'],
                            ra_sys_err=parset['ra_sys_err'],
                            dec_sys_err=parset['dec_sys_err'])

    logger.debug("Employing margin: %s extraction radius: %s deblend: %s deblend_nthresh: %s",
            parset['margin'],
            parset['radius'],
            parset['deblend'],
            parset['deblend_nthresh']
    )

    # Here we do the "blind" extraction of sources in the image
    results = data_image.extract()
    logger.info("Detected %d sources in image %s" % (len(results), image_path))

    return [r.serialize() for r in results]


def forced_fits(image_path, positions, parset_file):
    """Force fit ?? What does this do
    Args:
        - image_path: path to image
        - positions: ?
    """
    logger.info("Forced fitting in image: %s" % (image_path))
    fitsimage = tkp.utility.accessors.open(image_path)
    parset = parse_parset(parset_file)
    
    data_image = sourcefinder_image_from_accessor(fitsimage,
                            margin=parset['margin'], radius=parset['radius'],
                            detection_threshold=parset['detection_threshold'],
                            analysis_threshold=parset['analysis_threshold'],
                            ra_sys_err=parset['ra_sys_err'],
                            dec_sys_err=parset['dec_sys_err'])


    if len(positions):
        boxsize = BOX_IN_BEAMPIX * max(data_image.beam[0],data_image.beam[1])
        forced_fits = data_image.fit_fixed_positions(positions, boxsize)
        return [forced_fit.serialize() for forced_fit in forced_fits]
    else:
        return []
