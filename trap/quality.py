
import logging
from lofarpipe.support.parset import parameterset
from tkp.database import DataBase
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
from tkp.utility.accessors import FITSImage
import tkp.database.quality
import tkp.quality
from tkp.database.orm import Image

logger = logging.getLogger(__name__)

def parse_parset(parset_file):
    parset = parameterset(parset_file)
    result = {}
    result['sigma'] = parset.getInt('sigma', 3)
    result['f'] = parset.getInt('f', 4)
    result['low_bound'] = parset.getFloat('low_bound', 1)
    result['high_bound'] = parset.getInt('high_bound', 50)
    result['frequency'] = parset.getInt('frequency', 45*10**6)
    result['subbandwidth'] = parset.getInt('subbandwidth', 200*10**3)
    result['intgr_time'] = parset.getFloat('intgr_time', 18654)
    result['configuration'] = parset.getString('configuration', "LBA_INNER")
    result['subbands'] = parset.getInt('subbands', 10)
    result['channels'] = parset.getInt('channels', 64)
    result['ncore'] = parset.getInt('ncore', 24)
    result['nremote'] = parset.getInt('nremote',16)
    result['nintl'] = parset.getInt('nintl', 8)
    return result

def nice_format(f):
    if f > 9999 or f < 0.01:
        return "%.2e" % f
    else:
        return "%.2f" % f

def noise(image_id, parset_file):
    """ checks if an image passes the RMS quality check. If not, a rejection entry is added to the database.
    args:
        image_id: id of image in database
        parset_file: parset file location with quality check parameters
    Returns:
        True if image passes tests, false if not
    """
    database = DataBase()
    db_image = Image(database=database, id=image_id)
    fitsimage = FITSImage(db_image.url)
    p = parse_parset(parset_file)

    rms = rms_with_clipped_subregion(fitsimage.data, sigma=p['sigma'], f=p['f'])
    noise = noise_level(p['frequency'], p['subbandwidth'], p['intgr_time'],
        p['configuration'], p['subbands'], p['channels'],
        p['ncore'], p['nremote'], p['nintl'])

    if tkp.quality.rms_valid(rms, noise, low_bound=p['low_bound'], high_bound=p['high_bound']):
        logger.info("image %i accepted: rms: %s, theoretical noise: %s" % (db_image.id, nice_format(rms), nice_format(noise)))
        return True
    else:
        ratio = rms / noise
        reason = "rms value (%s) is %s times theoretical noise (%s)" % (nice_format(rms), nice_format(ratio), nice_format(noise))
        logger.info("image %s REJECTED: %s " % (db_image.id, reason) )
        tkp.database.quality.reject(database.connection, db_image.id,
            tkp.database.quality.reason['rms'], reason)
        return False
