import os
import logging
import json
from lofarpipe.support.lofarexceptions import PipelineException
from lofar.parameterset import parameterset
from tkp.database import DataBase, DataSet
from tkp.database.utils import monitoringlist as dbmon
import tkp.utility.accessors as accessors
from tkp.database.orm import Image

logger = logging.getLogger(__name__)

BOX_IN_BEAMPIX = 10 # TODO:  FIXME! (see also 'image' unit test)


def adjust_transients_in_monitoringlist(image_id, transients):
    dbmon.adjust_transients_in_monitoringlist(image_id, transients)


def forced_fits(null_detections, image):
    """
    Store the forced fits of the null detections 
    from the current image in extractedsources
    """
    forced_fits = []
    if len(null_detections) != 0:
        fitsimage = tkp.utility.accessors.open(image)
        # TODO ... parset ...
        data_image = sourcefinder_image_from_accessor(fitsimage)
        # TODO ... parset ...
        forced_fits = data_image.fit_fixed_positions(ff_nd[0], 
                            boxsize = BOX_IN_BEAMPIX * max(data_image.beam[0], data_image.beam[1]))
        # Remove the None items, results from sourcefinder for coordinates that couldn't be fit
        try:
            forced_fits.remove(None)
        except ValueError:
            pass
        #tuple_ff_nd = [forced_fit.serialize() for forced_fit in forced_fits]
        #dbmon.insert_forcedfits_into_extractedsource(db_image.id, tuple_ff_nd, extract='ff_nd')
    
    return forced_fits


def add_nulldetections(image_id):
    monitoringlist.add_nulldetections(image_id)


def mark_sources(dataset_id, parset):
    database = DataBase()
    dataset = DataSet(database=database, id = dataset_id)
    dataset.update_images()
    detection_thresh = parameterset(parset).getFloat('detection.threshold', 5)
    dataset.mark_transient_candidates(single_epoch_threshold=detection_thresh,
                                      combined_threshold=detection_thresh)


def update_monitoringlist(image_id):
    """ Update the monitoring list with newly found transients. 
    
    Transients that are already in the monitoring
    list will get their position updated from the runningcatalog.
    Args:
        - filename: FITS file
        - image_id: database image id
        - dataset_id: dataset to which the image belongs
    """
    database = DataBase()
    db_image = Image(database=database, id=image_id)
    if not os.path.exists(db_image.url):
        raise PipelineException("Image '%s' not found" % db_image.url)

    # Obtain the list of targets to be monitored (and not already
    # detected) for this image
    fitsimage = accessors.open(db_image.url)
    mon_targets = db_image.monitoringsources()

    # Run the source finder on these mon_targets
    if len(mon_targets):
        logger.info("Measuring %d undetected monitoring targets in image %s"
                    % (len(mon_targets), image_id))
        data_image = accessors.sourcefinder_image_from_accessor(fitsimage)
        print "UPDATE_MONITORINGLIST():", [(m.ra, m.decl) for m in mon_targets]
        print "UPDATE_MONITORINGLIST():", max(data_image.beam[0], data_image.beam[1])
        results = data_image.fit_fixed_positions(
            [(m.ra, m.decl) for m in mon_targets],
            boxsize=BOX_IN_BEAMPIX*max(data_image.beam[0], data_image.beam[1]))
        # Filter out the bad ones, and combines with xtrsrc_ids
        results = [(tgt.runcat, tgt.monitorid, result.serialize()) for tgt, result in
                   zip(mon_targets, results) if result is not None]
        db_image.insert_monitored_sources(results)


def add_manual_monitoringlist_entries(dataset_id, inputs):
    """Parses co-ords from self.inputs, loads them into the monitoringlist"""
    monitor_coords=[]
    if 'monitor_coords' in inputs:
        try:
            monitor_coords.extend(json.loads(inputs['monitor_coords']))
        except ValueError:
            logger.error("Could not parse monitor-coords from command line")
            return False

    if 'monitor_list' in inputs:
        try:
            mon_list = json.load(open(inputs['monitor_list']))
            monitor_coords.extend(mon_list)
        except ValueError:
            logger.error("Could not parse monitor-coords from file: "
                              +inputs['monitor_list'])
            return False

    if len(monitor_coords):
        logger.info( "You specified monitoring at coords:")
        for i in monitor_coords:
            logger.info( "RA, %f ; Dec, %f " % (i[0],i[1]))
    for c in monitor_coords:
        dataset = DataSet(id=dataset_id, database=DataBase())
        dataset.add_manual_entry_to_monitoringlist(c[0],c[1])
    return True
