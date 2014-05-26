import logging
import tkp.db
import tkp.quality
from tkp.quality.restoringbeam import beam_invalid
from tkp.quality.rms import rms_invalid
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.telescope.lofar.noise import noise_level
from tkp.utility import nice_format

logger = logging.getLogger(__name__)


def reject_check_lofar(accessor, parset):
    low_bound = parset['low_bound']
    high_bound = parset['high_bound']
    oversampled_x = parset['oversampled_x']
    elliptical_x = parset['elliptical_x']
    min_separation = parset['min_separation']

    if accessor.tau_time == 0:
        logger.info("image %s REJECTED: tau_time is 0, should be > 0" % accessor.url)
        return tkp.db.quality.reason['tau_time'], "tau_time is 0"

    rms = accessor.rms()
    noise = noise_level(accessor.freq_eff, accessor.freq_bw, accessor.tau_time,
        accessor.antenna_set, accessor.ncore, accessor.nremote, accessor.nintl
    )
    rms_check = rms_invalid(rms, noise, low_bound, high_bound)
    if not rms_check:
        logger.info("image %s accepted: rms: %s, theoretical noise: %s" % \
                        (accessor.url, nice_format(rms),
                         nice_format(noise)))
    else:
        logger.info("image %s REJECTED: %s " % (accessor.url, rms_check))
        return (tkp.db.quality.reason['rms'].id, rms_check)

    # beam shape check
    (semimaj, semimin, theta) = accessor.beam
    beam_check = beam_invalid(semimaj, semimin, theta, oversampled_x, elliptical_x)

    if not beam_check:
        logger.info("image %s accepted: semimaj: %s, semimin: %s" % (accessor.url,
                                             nice_format(semimaj),
                                             nice_format(semimin)))
    else:
        logger.info("image %s REJECTED: %s " % (accessor.url, beam_check))
        return (tkp.db.quality.reason['beam'].id, beam_check)

    # Bright source check
    bright = tkp.quality.brightsource.is_bright_source_near(accessor, min_separation)
    if bright:
        logger.info("image %s REJECTED: %s " % (accessor.url, bright))
        return (tkp.db.quality.reason['bright_source'].id, bright)