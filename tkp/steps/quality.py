import logging
from tkp.db.database import Database
from tkp.quality.restoringbeam import beam_invalid
from tkp.quality.rms import rms_invalid
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
from tkp.utility import nice_format
import tkp.utility.accessors
import tkp.db.quality
import tkp.quality.brightsource
import tkp.quality


logger = logging.getLogger(__name__)


def reject_check(image_path, parset):
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

    sigma = parset['sigma']
    f = parset['f']
    low_bound = parset['low_bound']
    high_bound = parset['high_bound']
    oversampled_x = parset['oversampled_x']
    elliptical_x = parset['elliptical_x']
    min_separation = parset['min_separation']

    # RMS value check
    rms = rms_with_clipped_subregion(accessor.data, sigma, f)
    lofar_metadata = accessor.extra_metadata
    noise = noise_level(accessor.freq_eff, accessor.freq_bw, accessor.tau_time,
                    lofar_metadata['antenna_set'], lofar_metadata['ncore'],
                    lofar_metadata['nremote'], lofar_metadata['nintl'])
    rms_check = rms_invalid(rms, noise, low_bound, high_bound)
    if not rms_check:
        logger.info("image %s accepted: rms: %s, theoretical noise: %s" % \
                        (image_path, nice_format(rms),
                         nice_format(noise)))
    else:
        logger.info("image %s REJECTED: %s " % (image_path, rms_check))
        return (tkp.db.quality.reason['rms'].id, rms_check)

    # beam shape check
    (semimaj, semimin, theta) = accessor.beam
    beam_check = beam_invalid(semimaj, semimin, oversampled_x, elliptical_x)

    if not beam_check:
        logger.info("image %s accepted: semimaj: %s, semimin: %s" % (image_path,
                                             nice_format(semimaj),
                                             nice_format(semimin)))
    else:
        logger.info("image %s REJECTED: %s " % (image_path, beam_check))
        return (tkp.db.quality.reason['beam'].id, beam_check)

    # Bright source check
    bright = tkp.quality.brightsource.is_bright_source_near(accessor, min_separation)
    if bright:
        logger.info("image %s REJECTED: %s " % (image_path, bright))
        return (tkp.db.quality.reason['bright_source'].id, bright)


def reject_image(image_id, reason, comment):
    """
    Adds a rejection for an image to the database

    NOTE: should only be used on a MASTER node
    """
    tkp.db.quality.reject(image_id, reason, comment)


