import os
import logging
from lofarpipe.support.lofarexceptions import PipelineException
import tkp.utility.accessors
from tkp.utility.accessors import sourcefinder_image_from_accessor
from lofar.parameterset import parameterset

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

    
def forced_fits(image_path, positions):
    """Force fit ?? What does this do
    Args:
        - image_path: path to image
        - positions: ?
    """
    if not os.path.exists(image_path):
        raise PipelineException("Image '%s' not found" % image_path)
    fitsimage = tkp.utility.accessors.open(image_path)
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
    return [forced_fit.serialize() for forced_fit in forced_fits]
