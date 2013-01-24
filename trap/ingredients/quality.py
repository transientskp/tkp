
import logging
import datetime
from lofarpipe.support.parset import parameterset
from tkp.database import DataBase, query
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.utility.accessors
import tkp.database.quality
import tkp.quality.brightsource
import tkp.quality
from tkp.database.orm import Image

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


def check(image_id, parset_file):
    """ checks if an image passes the quality check. If not, a rejection
        entry is added to the database.
    args:
        image_id: id of image in database
        parset_file: parset file location with quality check parameters
    Returns:
        True if image passes tests, false if not
    """
    database = DataBase()
    db_image = Image(database=database, id=image_id)
    accessor = tkp.utility.accessors.open(db_image.url)
    p = parse_parset(parset_file)

    # TODO: this is getting messy and can use a cleanup

    rms = rms_with_clipped_subregion(accessor.data, sigma=p['sigma'], f=p['f'])
    noise = noise_level(accessor.freq_eff, accessor.freq_bw, accessor.tau_time,
        accessor.antenna_set, accessor.subbands, accessor.channels,
        accessor.ncore, accessor.nremote, accessor.nintl)

    rms_invalid = tkp.quality.rms_invalid(rms, noise, low_bound=p['low_bound'],
        high_bound=p['high_bound'])
    if not rms_invalid:
        logger.info("image %i accepted: rms: %s, theoretical noise: %s" % \
                        (db_image.id, tkp.quality.nice_format(rms),
                         tkp.quality.nice_format(noise)))
    else:
        logger.info("image %s REJECTED: %s " % (db_image.id, rms_invalid) )
        tkp.database.quality.reject(database.connection, db_image.id,
                    tkp.database.quality.reason['rms'].id, rms_invalid)
        return False

    (semimaj, semimin, theta) = accessor.beam
    beam_invalid = tkp.quality.beam_invalid(semimaj, semimin,
                                        p['oversampled_x'], p['elliptical_x'])

    if not beam_invalid:
        logger.info("image %i accepted: semimaj: %s, semimin: %s" % (db_image
                                                                   .id,
                                             tkp.quality.nice_format(semimaj),
                                             tkp.quality.nice_format(semimin)))
    else:
        logger.info("image %s REJECTED: %s " % (db_image.id, beam_invalid) )
        tkp.database.quality.reject(database.connection, db_image.id,
                            tkp.database.quality.reason['beam'].id, beam_invalid)
        return False

    bright_source_near = tkp.quality.brightsource.is_bright_source_near(accessor,
                                            p['min_separation'])

    if bright_source_near:
        logger.info("image %s REJECTED: %s " % (db_image.id, bright_source_near) )
        tkp.database.quality.reject(database.connection, db_image.id,
            tkp.database.quality.reason['bright_source'].id, bright_source_near)
        return False

    return True
