
import logging
from lofarpipe.support.parset import parameterset
from tkp.database import DataBase
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.utility.accessors
import tkp.database.quality
import tkp.quality.brightsource
import tkp.quality
from tkp.database.orm import Image

logger = logging.getLogger(__name__)

def parse_parset(parset_file, accessor=None):
    """parse the quality parset file. uses accessor for default values"""
    parset = parameterset(parset_file)
    result = {}
    result['sigma'] = parset.getInt('sigma', 3)
    result['f'] = parset.getInt('f', 4)
    result['low_bound'] = parset.getFloat('low_bound', 1)
    result['high_bound'] = parset.getInt('high_bound', 50)
    result['oversampled_x'] = parset.getInt('oversampled_x', 30)
    result['elliptical_x'] = parset.getFloat('elliptical_x', 2.0)
    result['min_separation'] = parset.getFloat('min_separation', 20)

    # LOFAR image properties - first check if set in parset, if not get value
    # from image, if not set use default
    freq_eff = getattr(accessor,'freq_eff', None) or 45*10**6
    result['freq_eff'] = parset.getFloat('freq_eff', freq_eff)

    subbandwidth = getattr(accessor, 'subbandwidth', None) or 200*10**3
    result['subbandwidth'] = parset.getFloat('subbandwidth', subbandwidth)

    intgr_time = getattr(accessor, 'intgr_time', None) or 18654
    result['intgr_time'] = parset.getFloat('intgr_time', intgr_time)

    antenna_set = getattr(accessor, 'antenna_set', "LBA_INNER") or "LBA_INNER"
    result['antenna_set'] = parset.getString('antenna_set', antenna_set)

    subbands = getattr(accessor, 'subbands', None) or 10
    result['subbands'] = parset.getInt('subbands', subbands)

    channels = getattr(accessor, 'channels', None) or 64
    result['channels'] = parset.getInt('channels', channels)

    ncore = getattr(accessor, 'ncore', None) or 24
    result['ncore'] = parset.getInt('ncore', ncore)

    nremote = getattr(accessor, 'nremote', None) or 16
    result['nremote'] = parset.getInt('nremote', nremote)

    nintl =  getattr(accessor, 'nintl', None) or 8
    result['nintl'] = parset.getInt('nintl', nintl)

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
    noise = noise_level(p['freq_eff'], p['subbandwidth'], p['intgr_time'],
        p['antenna_set'], p['subbands'], p['channels'],
        p['ncore'], p['nremote'], p['nintl'])

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
