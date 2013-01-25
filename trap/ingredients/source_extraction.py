import os
import logging
from contextlib import closing
from lofarpipe.support.lofarexceptions import PipelineException

from lofar.parameterset import parameterset
from tkp.database import DataBase
from tkp.database.orm import Image
from tkp.database.utils import general
from tkp.database.utils import monitoringlist

logger = logging.getLogger(__name__)

BOX_IN_BEAMPIX = 10 # TODO:  FIXME! (see also 'image' unit test)

def extract_sources(image_path, parset, tkpconfigdir = None):
    """Extract sources from an image
    Args:
        - image_path: path to file to extract sources from
        - parset: parameter set *filename* containing at least the
                detection and analysis threshold and the association radius,
                the last one a multiplication factor of the de Ruiter radius.
        - tkpconfigdir:
    """

    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
    import tkp
    from tkp.config import config
    import tkp.utility.accessors
    from tkp.utility.accessors import sourcefinder_image_from_accessor
   
    results = []
    if not os.path.exists(image_path):
        raise PipelineException("Image '%s' not found" % image_path)
    logger.info("Extracting image: %s" % (image_path))
    fitsimage = tkp.utility.accessors.open(image_path)
    seconfig = config['source_extraction']
    #logger.info("SE seconfig: %s" % (seconfig,))
    #logger.info("SE parset: %s" % (parset,))
    parset = parameterset(parset)

    logger.debug("Detecting sources in image %s at detection threshold %s",
        image_path, parset.getFloat('detection.threshold'))

    data_image = sourcefinder_image_from_accessor(fitsimage)

    # TODO: Why do we have this here?
    seconfig['back_sizex'] = parset.getInt('backsize.x',
        seconfig['back_sizex'])
    seconfig['back_sizey'] = parset.getInt('backsize.y',
        seconfig['back_sizey'])
    seconfig['margin'] = parset.getFloat('margin',
        seconfig['margin'])
    seconfig['deblend'] = parset.getBool('deblend',
        seconfig['deblend'])
    seconfig['deblend_nthresh'] = parset.getInt('deblend_nthresh',
        seconfig['deblend_nthresh'])
    seconfig['radius'] = parset.getFloat('radius',
        seconfig['radius'])
    seconfig['ra_sys_err'] = parset.getFloat('ra.sys.err',
        seconfig['ra_sys_err'])
    seconfig['dec_sys_err'] = parset.getFloat('dec.sys.err',
        seconfig['dec_sys_err'])


    logger.debug("Employing margin: %s extraction radius: %s deblend: %s "
                "deblend_nthresh: %s",
        seconfig['margin'],
        seconfig['radius'],
        seconfig['deblend'],
        seconfig['deblend_nthresh']
    )

    det = parset.getFloat('detection.threshold',
        seconfig['detection_threshold'])
    anl = parset.getFloat('analysis.threshold',
        seconfig['analysis_threshold'])

    ##Finally, do some work!
    # Here we do the "blind" extraction of sources in the image
    results = data_image.extract(det=det, anl=anl)
    logger.info("Detected %d sources in image %s" % (len(results), image_path))
    
    return [r.serialize() for r in results]

    
def forced_fits(image, positions, parset, tkpconfigdir = None):
    """Extract sources from a FITS image
    Args:
        - database: the instance to access the database
        - image_id: the image id under which the image is known in the database
        - parset: parameter set *filename* containing at least the
                detection and analysis threshold and the association radius,
                the last one a multiplication factor of the de Ruiter radius.
        - tkpconfigdir:
    """


    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
    import tkp
    from tkp.config import config
    import tkp.utility.accessors
    from tkp.utility.accessors import sourcefinder_image_from_accessor
   
    if not os.path.exists(image):
        raise PipelineException("Image '%s' not found" % image)
    fitsimage = tkp.utility.accessors.open(image)
    data_image = sourcefinder_image_from_accessor(fitsimage)
    
    forced_fits = []
    if len(positions) != 0:
        forced_fits = data_image.fit_fixed_positions(positions[0], 
                        boxsize = BOX_IN_BEAMPIX * max(data_image.beam[0], data_image.beam[1]))
        # Remove the None items, results from sourcefinder for coordinates that couldn't be fit
        try:
            forced_fits.remove(None)
        except ValueError:
            pass
    return {'forced_fits': [forced_fit.serialize() for forced_fit in forced_fits]}
    
    
    
    
#    tuple_results = [result.serialize() for result in results]
#    # Add the blindly extracted sources from sourcefinder
#    # to extractedsource. These are extract_type = 0 (default) sources.
#    db_image.insert_extracted_sources(tuple_results)
#    
#    # Select null detections in the current image for a forced fit,
#    # i.e. those sources that are in runcat and are expected to be detected, 
#    # but weren't. These are extract_type = 1 sources.
#    # TODO: This is easy if we assume images are from the same region and of the 
#    # same quality (flux levels, etc). What if not?
#    ff_nd = monitoringlist.forced_fit_null_detections(db_image.id)
#    if len(ff_nd) != 0:
#        forced_fits = data_image.fit_fixed_positions(ff_nd[0], 
#                        boxsize = BOX_IN_BEAMPIX * max(data_image.beam[0], data_image.beam[1]))
#        # Remove the None items, results from sourcefinder for coordinates that couldn't be fit
#        try:
#            forced_fits.remove(None)
#        except ValueError:
#            pass
#        tuple_ff_nd = [forced_fit.serialize() for forced_fit in forced_fits]
#        monitoringlist.insert_forcedfits_into_extractedsource(db_image.id, tuple_ff_nd, extract='ff_nd')
#    
#    # Select the user-entry sources in the monitoringlist for a forced fit,
#    # as well as those sources already in the monitoringlist, but which do 
#    # not have a counterpart among the blindly extractedsources. 
#    # These are extract_type = 2 sources
#    # NOTE: Do not swap the sequence of ff_nd and ff_mon
#    ff_mon = monitoringlist.forced_fit_monsources(db_image.id)
#    if len(ff_mon) != 0:
#        forced_fits = data_image.fit_fixed_positions(ff_mon[0],
#                        boxsize=BOX_IN_BEAMPIX*max(data_image.beam[0], data_image.beam[1]))
#        # Remove the None items, results from sourcefinder for coordinates that couldn't be fit
#        try:
#            forced_fits.remove(None)
#        except ValueError:
#            pass
#        tuple_ff_mon = [forced_fit.serialize() for forced_fit in forced_fits]
#        monitoringlist.insert_forcedfits_into_extractedsource(db_image.id, tuple_ff_mon, extract='ff_mon')
#    
#    # All extractedsources are ready to be associated w/ runcat
#    deRuiter_r = (parset.getFloat('association.radius') *
#                  config['source_association']['deRuiter_radius'])
#    db_image.associate_extracted_sources(deRuiter_r=deRuiter_r)
#    
#    return db_image.id

