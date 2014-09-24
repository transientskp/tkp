import logging
import tkp.accessors
from tkp.accessors import sourcefinder_image_from_accessor
import tkp.accessors
from collections import namedtuple

logger = logging.getLogger(__name__)

#Short-lived struct for returning results from the source extraction routine:
ExtractionResults = namedtuple('ExtractionResults',
                                   ['sources',
                                    'rms_min',
                                    'rms_max'])


def extract_sources(image_path, extraction_params):
    """
    Extract sources from an image.

    args:
        image_path: path to file from which to extract sources.
        extraction_params: dictionary containing at least the detection and
            analysis threshold and the association radius, the last one a
            multiplication factor of the de Ruiter radius.
    returns:
        list of ExtractionResults named tuples containing source measurements,
        min RMS value and max RMS value
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
    results = data_image.extract(
        det=extraction_params['detection_threshold'],
        anl=extraction_params['analysis_threshold'],
        deblend_nthresh=extraction_params['deblend_nthresh'],
        force_beam=extraction_params['force_beam']
    )
    logger.info("Detected %d sources in image %s" % (len(results), image_path))

    ew_sys_err = extraction_params['ew_sys_err']
    ns_sys_err = extraction_params['ns_sys_err']
    serialized = [r.serialize(ew_sys_err, ns_sys_err) for r in results]
    return ExtractionResults(sources=serialized,
                             rms_min=float(data_image.rmsmap.min()),
                             rms_max=float(data_image.rmsmap.max())
                             )


def forced_fits(image_path, positions, ids, extraction_params):
    """
    Perform forced source measurements on an image based on a list of
    positions.

    Args:
        image_path (str): path to image for measurements.
        positions (list of (RA, Dec) 2-tuples): positions to be fit.
        ids: List of identifiers for each requested fit position.
        extraction_params (dict): source extraction parameters, as a dictionary.

    Returns:
        A matched pair of lists (serialized_fits, ids), corresponding to
        successfully fitted positions.
        NB returned lists may be shorter than input lists
        if some fits are unsuccessful.
    """
    logger.info("Forced fitting in image: %s" % (image_path))
    fitsimage = tkp.accessors.open(image_path)

    data_image = sourcefinder_image_from_accessor(fitsimage,
                    margin=extraction_params['margin'],
                    radius=extraction_params['extraction_radius_pix'],
                    back_size_x=extraction_params['back_size_x'],
                    back_size_y=extraction_params['back_size_y'])

    boxsize = extraction_params['box_in_beampix'] * max(data_image.beam[0],
                                             data_image.beam[1])
    #forced_fits = data_image.fit_fixed_positions(positions, boxsize)
    successful_fits, successful_ids = data_image.fit_fixed_positions(
                                                positions, boxsize, ids=ids)
    if successful_fits:
        serialized = [
            f.serialize(
                extraction_params['ew_sys_err'], extraction_params['ns_sys_err']
                ) for f in successful_fits]
        return serialized, successful_ids
    else:
        return [],[]
