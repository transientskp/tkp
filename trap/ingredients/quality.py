
import logging
from lofarpipe.support.parset import parameterset
from tkp.database import DataBase
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.utility.accessors
import tkp.database.quality
import tkp.quality.brightsource
import tkp.quality


logger = logging.getLogger(__name__)


def parse_parset(parset_file):
    """parse the quality parset file."""
    parset = parameterset(parset_file)
    result = {}
    result['sigma'] = parset.getInt('sigma', 3)
    result['f'] = parset.getInt('f', 4)
    result['low_bound'] = parset.getFloat('low_bound', 1)
    result['high_bound'] = parset.getInt('high_bound', 50)
    result['oversampled_x'] = parset.getInt('oversampled_x', 30)
    result['elliptical_x'] = parset.getFloat('elliptical_x', 2.0)
    result['min_separation'] = parset.getFloat('min_separation', 20)
    return result


def reject_check(id, image_path, parset_file):
    """ checks if an image passes the quality check. If not, a rejection
        tuple is returned.

    NOTE: should only be used on a NODE

    args:
        id: database ID of image. This is not used but kept as a reference for
            distributed computation!
        image_path: path to image
        parset_file: parset file location with quality check parameters
    Returns:
        (rejection ID, description) if rejected, else None
    """

    accessor = tkp.utility.accessors.open(image_path)
    p = parse_parset(parset_file)

    rms = rms_with_clipped_subregion(accessor.data, sigma=p['sigma'], f=p['f'])
    noise = noise_level(accessor.freq_eff, accessor.freq_bw, accessor.tau_time,
        accessor.antenna_set, accessor.subbands, accessor.channels,
        accessor.ncore, accessor.nremote, accessor.nintl)

    rms_invalid = tkp.quality.rms_invalid(rms, noise, low_bound=p['low_bound'],
        high_bound=p['high_bound'])
    
    if not rms_invalid:
        logger.info("image %s accepted: rms: %s, theoretical noise: %s" % \
                        (image_path, tkp.quality.nice_format(rms),
                         tkp.quality.nice_format(noise)))
    else:
        logger.info("image %s REJECTED: %s " % (image_path, rms_invalid) )
        return (tkp.database.quality.reason['rms'].id, rms_invalid)

    (semimaj, semimin, theta) = accessor.beam
    beam_invalid = tkp.quality.beam_invalid(semimaj, semimin,
                                        p['oversampled_x'], p['elliptical_x'])

    if not beam_invalid:
        logger.info("image %s accepted: semimaj: %s, semimin: %s" % (image_path,
                                             tkp.quality.nice_format(semimaj),
                                             tkp.quality.nice_format(semimin)))
    else:
        logger.info("image %s REJECTED: %s " % (image_path, beam_invalid) )
        return (tkp.database.quality.reason['beam'].id, beam_invalid)

    bright_source_near = tkp.quality.brightsource.is_bright_source_near(accessor,
                                            p['min_separation'])

    if bright_source_near:
        logger.info("image %s REJECTED: %s " % (image_path, bright_source_near) )
        return (id, tkp.database.quality.reason['bright_source'].id, bright_source_near)


def reject_image(image_id, reason, comment):
    """
    Adds a rejection for an image to the database

    NOTE: should only be used on a MASTER node
    """
    tkp.database.quality.reject(image_id, reason, comment)


