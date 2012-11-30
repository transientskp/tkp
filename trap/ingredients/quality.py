
import logging
from lofarpipe.support.parset import parameterset
from tkp.database import DataBase
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
import tkp.utility.accessors
import tkp.database.quality
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

    # LOFAR image properties - first check if set in parset, if not get value
    # from image, if not set use default
    result['frequency'] = parset.getInt('frequency',
                            getattr(accessor,'frequency', 45*10**6))
    result['subbandwidth'] = parset.getInt('subbandwidth',
                            getattr(accessor, 'subbandwidth', 200*10**3))
    result['intgr_time'] = parset.getFloat('intgr_time',
                            getattr(accessor, 'intgr_time', 18654))
    result['configuration'] = parset.getString('configuration',
                            getattr(accessor, 'configuration', "LBA_INNER"))
    result['subbands'] = parset.getInt('subbands',
                            getattr(accessor, 'subbands', 10))
    result['channels'] = parset.getInt('channels',
                            getattr(accessor, 'channels', 64))
    result['ncore'] = parset.getInt('ncore',
                            getattr(accessor, 'ncore', 24))
    result['nremote'] = parset.getInt('nremote',
                            getattr(accessor, 'nremote', 16))
    result['nintl'] = parset.getInt('nintl',
                            getattr(accessor, 'nintl', 8))

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

    rms = rms_with_clipped_subregion(accessor.data, sigma=p['sigma'], f=p['f'])
    noise = noise_level(p['frequency'], p['subbandwidth'], p['intgr_time'],
        p['configuration'], p['subbands'], p['channels'],
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
                            tkp.database.quality.reason['rms'].id, beam_invalid)
        return False

    return True
