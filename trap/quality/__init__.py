
import logging
from lofarpipe.support.parset import parameterset
from tkp.database import DataBase, DataSet
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.lofar.noise import noise_level
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import dbimage_from_accessor
import tkp.database.quality
import tkp.quality

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

def noise(image, dataset_id, parset_file):
    """ checks if an image passes the RMS quality check. If not, a rejection entry is added to the database.
    args:
        fitsimage: a fitsimage accessor
        db_image: a database image object
        database: a tkp database object
    Returns:
        image database ID if the images passes the test, None otherwise
    """
    database = DataBase()
    dataset = DataSet(id=dataset_id, database=database)
    fitsimage = FITSImage(image)
    db_image = dbimage_from_accessor(dataset=dataset,  image=fitsimage)
    p = parse_parset(parset_file)

    rms = rms_with_clipped_subregion(fitsimage.data, sigma=p['sigma'], f=p['f'])
    noise = noise_level(p['frequency'], p['subbandwidth'], p['intgr_time'],
                        p['configuration'], p['subbands'], p['channels'],
                        p['ncore'], p['nremote'], p['nintl'])

    if tkp.quality.rms_valid(rms, noise, low_bound=p['low_bound'], high_bound=p['high_bound']):
        return db_image.id
    else:
        ratio = rms / noise
        reason = "noise level is %s times theoretical value" % ratio
        logging.info("image %s invalid: %s " % (db_image.id, reason) )
        tkp.database.quality.reject(database.connection, db_image.id,
            tkp.database.quality.reason['rms'], reason)
        return None