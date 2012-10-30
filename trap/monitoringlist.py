import os
import logging
from lofarpipe.support.lofarexceptions import PipelineException
from lofar.parameterset import parameterset
from tkp.database import DataBase, DataSet
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import sourcefinder_image_from_accessor
from lofarpipe.support.utilities import log_time
from tkp.database.orm import Image

logger = logging.getLogger(__name__)

BOX_IN_BEAMPIX = 10 # TODO:  FIXME! (see also 'image' unit test)

def mark_sources(dataset_id, parset):
    database = DataBase()
    dataset = DataSet(database=database, id = dataset_id)
    dataset.update_images()
    detection_thresh = parameterset(parset).getFloat('detection.threshold', 5)
    dataset.mark_transient_candidates(single_epoch_threshold = detection_thresh, combined_threshold = detection_thresh)

def update_monitoringlist(image_id):
    """ Update the monitoring list with newly found transients. Transients that are already in the monitoring
    list will get their position updated from the runningcatalog.
    Args:
        - filename: FITS file
        - image_id: database image id
        - dataset_id: dataset to which the image belongs
    """

    log_time(logger)
    database = DataBase()
    db_image = Image(database=database, id=image_id)
    if not os.path.exists(db_image.url):
        raise PipelineException("Image '%s' not found" % db_image.url)


    # Obtain the list of sources to be monitored (and not already
    # detected) for this image
    fitsimage = FITSImage(db_image.url)
    sources = db_image.monitoringsources()

    # Run the source finder on these sources
    if len(sources):
        logger.info("Measuring %d undetected monitoring sources." % (len(sources),))
        data_image = sourcefinder_image_from_accessor(fitsimage)
        results = data_image.fit_fixed_positions(
            [(source[0], source[1]) for source in sources],
            boxsize=BOX_IN_BEAMPIX*max(data_image.beam[0], data_image.beam[1]))
        # Filter out the bad ones, and combines with xtrsrc_ids
        results = [(source[2], source[3], result.serialize()) for source, result in
                   zip(sources, results) if result is not None]
        db_image.insert_monitored_sources(results)