import logging
from tkp.database import DataBase, DataSet
from tkp.database import Image as DBImage
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import sourcefinder_image_from_accessor
from lofarpipe.support.utilities import log_time

logger = logging.getLogger(__name__)

BOX_IN_BEAMPIX = 10 # TODO:  FIXME! (see also 'image' unit test)

def monitoringlist(filename, image_id, dataset_id):
    """ Update the monitoring list with newly found transients. Transients that are already in the monitoring
    list will get their position updated from the runningcatalog.
    Args:
        - filename: FITS file
        - image_id: database image id
        - dataset_id: dataset to which the image belongs
    """

    log_time(logger)
    database = DataBase()
    # Obtain the list of sources to be monitored (and not already
    # detected) for this image
    fitsimage = FITSImage(filename)

    ##TO DO: would prefer it if there were an easy way for the image
    ## to determine its parent dataset without being spoon fed.
    ## -This would cut down on required recipe arguments and generally
    ##    make it harder to screw up.
    dataset = DataSet(id = dataset_id, database=database)
    db_image = DBImage(id=image_id, database=database, dataset=dataset)
    #                db_image.update()
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