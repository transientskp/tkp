import logging
import tkp.accessors
from tkp.accessors import sourcefinder_image_from_accessor, detection
import tkp.accessors
from collections import namedtuple


logger = logging.getLogger(__name__)

class ExtractionResults(namedtuple('ExtractionResults',
                                   ['sources',
                                    'rms_min',
                                    'rms_max',
                                    'detection_thresh',
                                    'analysis_thresh'])):
    pass
    """
    Used for returning a bunch of results from the source extraction routine.

    (In a clear and maintainable fashion.)
    """



def extract_sources(image_path, extraction_params):
    """
    Extract sources from an image.

    args:
        image_path: path to file from which to extract sources.
        extraction_params: dictionary containing at least the detection and
            analysis threshold and the association radius, the last one a
            multiplication factor of the de Ruiter radius.
    returns:
        list of source measurements, min RMS value, max RMS value
    """
    logger.info("Extracting image: %s" % image_path)
    accessor = tkp.accessors.open(image_path)
    logger.debug("Detecting sources in image %s at detection threshold %s",
                 image_path, extraction_params['detection_threshold'])
    data_image = sourcefinder_image_from_accessor(accessor,
                    margin=extraction_params['margin'],
                    radius=extraction_params['extraction_radius_pix'],
                    back_size_x=extraction_params['back_size_x'],
                    back_size_y=extraction_params['back_size_y'])

    logger.debug("Employing margin: %s extraction radius: %s deblend_nthresh: %s",
                 extraction_params['margin'],
                 extraction_params['extraction_radius_pix'],
                 extraction_params['deblend_nthresh']
    )

    # "blind" extraction of sources
    detection_thresh =extraction_params['detection_threshold']
    analysis_thresh = extraction_params['analysis_threshold']
    results = data_image.extract(
        det=detection_thresh,
        anl=analysis_thresh,
        deblend_nthresh=extraction_params['deblend_nthresh'],
        force_beam=extraction_params['force_beam']
    )
    logger.info("Detected %d sources in image %s" % (len(results), image_path))

    ew_sys_err = extraction_params['ew_sys_err']
    ns_sys_err = extraction_params['ns_sys_err']
    serialized = [r.serialize(ew_sys_err, ns_sys_err) for r in results]
    return ExtractionResults(sources=serialized,rms_min=data_image.rmsmap.min(),
                     rms_max=data_image.rmsmap.max(),
                     detection_thresh=detection_thresh,
                     analysis_thresh=analysis_thresh,
                     )


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
                    back_size_x=extraction_params['back_size_x'],
                    back_size_y=extraction_params['back_size_y'])

    if len(positions):
        boxsize = extraction_params['box_in_beampix'] * max(data_image.beam[0],
                                                 data_image.beam[1])
        forced_fits = data_image.fit_fixed_positions(positions, boxsize)
        return [
            forced_fit.serialize(
                extraction_params['ew_sys_err'], extraction_params['ns_sys_err']
            ) for forced_fit in forced_fits
        ]
    else:
        return []
