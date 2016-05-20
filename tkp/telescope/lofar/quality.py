import logging
import tkp.db
import tkp.db.quality as dbquality
from tkp.quality.restoringbeam import beam_invalid
from tkp.quality.rms import rms_invalid
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.telescope.lofar.noise import noise_level
from tkp.utility import nice_format

logger = logging.getLogger(__name__)


def reject_check_lofar(accessor, job_config):

    lofar_quality_params = job_config['quality_lofar']

    low_bound = lofar_quality_params['low_bound']
    high_bound = lofar_quality_params['high_bound']
    oversampled_x = lofar_quality_params['oversampled_x']
    elliptical_x = lofar_quality_params['elliptical_x']
    min_separation = lofar_quality_params['min_separation']

    if accessor.tau_time == 0:
        logger.info("image %s REJECTED: tau_time is 0, should be > 0" % accessor.url)
        return dbquality.reject_reasons['tau_time'], "tau_time is 0"

    rms_est_sigma = job_config.persistence.rms_est_sigma
    rms_est_fraction = job_config.persistence.rms_est_fraction
    rms_qc = rms_with_clipped_subregion(accessor.data,
                                        rms_est_sigma=rms_est_sigma,
                                        rms_est_fraction=rms_est_fraction)

    noise = noise_level(accessor.freq_eff, accessor.freq_bw, accessor.tau_time,
        accessor.antenna_set, accessor.ncore, accessor.nremote, accessor.nintl
    )
    rms_check = rms_invalid(rms_qc, noise, low_bound, high_bound)
    if not rms_check:
        logger.info("image %s accepted: rms: %s, theoretical noise: %s" % \
                        (accessor.url, nice_format(rms_qc),
                         nice_format(noise)))
    else:
        logger.info("image %s REJECTED: %s " % (accessor.url, rms_check))
        return (dbquality.reject_reasons['rms'], rms_check)

    # beam shape check
    (semimaj, semimin, theta) = accessor.beam
    beam_check = beam_invalid(semimaj, semimin, theta, oversampled_x, elliptical_x)

    if not beam_check:
        logger.info("image %s accepted: semimaj: %s, semimin: %s" % (accessor.url,
                                             nice_format(semimaj),
                                             nice_format(semimin)))
    else:
        logger.info("image %s REJECTED: %s " % (accessor.url, beam_check))
        return (dbquality.reject_reasons['beam'], beam_check)

    # Bright source check
    bright = tkp.quality.brightsource.is_bright_source_near(accessor, min_separation)
    if bright:
        logger.info("image %s REJECTED: %s " % (accessor.url, bright))
        return (dbquality.reject_reasons['bright_source'], bright)