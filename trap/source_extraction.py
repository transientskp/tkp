import os
import logging
from lofarpipe.support.lofarexceptions import PipelineException
from lofarpipe.support.utilities import log_time
from lofar.parameterset import parameterset
from tkp.database import DataBase
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import sourcefinder_image_from_accessor
from tkp.database.orm import Image

logger = logging.getLogger(__name__)

def extract_sources(image_id, parset, tkpconfigdir=None):
    """Extract sources from a FITS image
    Args:
        - image: FITS filename
        - dataset_id: dataset to which image belongs
        - parset: parameter set *filename* containg at least the
              detection threshold and the source association
              radius, the last one in units of the de Ruiter
              radius.
    """

    log_time(logger)

    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
    from tkp.config import config

    database = DataBase()
    db_image = Image(database=database, id=image_id)
    if not os.path.exists(db_image.url):
        raise PipelineException("Image '%s' not found" % db_image.url)
    fitsimage = FITSImage(db_image.url)
    seconfig = config['source_extraction']
    parset = parameterset(parset)

    logger.info("Detecting sources in %s at %f level", db_image.url, parset.getFloat('detection.threshold'))
    data_image = sourcefinder_image_from_accessor(fitsimage)
    seconfig['back_sizex'] = parset.getInt('backsize.x', seconfig['back_sizex'])
    seconfig['back_sizey'] = parset.getInt('backsize.y', seconfig['back_sizey'])
    seconfig['margin'] = parset.getFloat('margin', seconfig['margin'])
    seconfig['deblend'] = parset.getBool('deblend', seconfig['deblend'])
    seconfig['deblend_nthresh'] = parset.getInt('deblend_nthresh', seconfig['deblend_nthresh'])

    logger.info("Employing margin: %f, deblend: %s, deblend_nthresh:%d",
        seconfig['margin'],
        seconfig['deblend'],
        seconfig['deblend_nthresh']
    )

    det = parset.getFloat('detection.threshold',
        seconfig['detection_threshold'])
    anl = parset.getFloat('analysis.threshold',
        seconfig['analysis_threshold'])

    ##Finally, do some work!
    results = data_image.extract(det=det, anl=anl)

    logger.info("Detected %d sources", len(results))
    logger.info("Saving extracted sources to database")
    tuple_results = [result.serialize() for result in results]
    db_image.insert_extracted_sources(tuple_results)
    deRuiter_r = (parset.getFloat('association.radius') *
                  config['source_association']['deruiter_radius'])
    logger.info("Associate newly extracted sources with existing ones")
    db_image.associate_extracted_sources(deRuiter_r=deRuiter_r)
    #self.logger.info("Update monitoring list for already found sources")
    #db_image.match_monitoringlist(assoc_r=deRuiter_r, mindistance=30)

    return db_image.id

