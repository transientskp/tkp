"""
This `step` is used for the storing of images and metadata
to the database
"""
import os
import logging
import cPickle
from tempfile import NamedTemporaryFile
from astropy.io.fits import open as fits_open
from casacore.images import image as casacore_image

import tkp.accessors
from tkp.db.database import Database
from tkp.db.orm import DataSet, Image
from tkp.quality.rms import rms_with_clipped_subregion

logger = logging.getLogger(__name__)


def create_dataset(dataset_id, description):
    """ Creates a dataset if it doesn't exists
    Note: Should only be used in a master recipe
    Returns:
      the database ID of this dataset
    """
    database = Database()
    if dataset_id == -1:
        dataset = DataSet({'description': description}, database)
        logger.info("created dataset %s (%s)" % (dataset.id,
                                                  dataset.description))
    else:
        dataset = DataSet(id=dataset_id, database=database)
        logger.info("using dataset %s (%s)" % (dataset.id,
                                                dataset.description))
    return dataset.id


def extract_metadatas(accessors, rms_est_sigma, rms_est_fraction):
    """
    Extracts metadata and rms_qc values from the list of images.

    Args:
        accessors: list of image accessors
        rms_est_sigma: used for RMS calculation, see `tkp.quality.statistics`
        rms_est_fraction: used for RMS calculation, see `tkp.quality.statistics`

    Returns:
        a list of metadata's. The metadata will be False if extraction failed.
    """
    results = []
    for accessor in accessors:
        logger.debug("Extracting metadata from %s" % accessor.url)
        metadata = accessor.extract_metadata()
        metadata['rms_qc'] = rms_with_clipped_subregion(accessor.data,
                                                        rms_est_sigma,
                                                        rms_est_fraction)
        results.append(metadata)
    return results


def store_images_in_db(images_metadata, extraction_radius_pix, dataset_id, bandwidth_max):
    """ Add images to database.
    Note that all images in one dataset should be inserted in one go, since the
    order is very important here. If you don't add them all in once, you should
    make sure they are added in the correct order e.g. sorted by observation
    time.

    Note: Should only be used in a master recipe

    Args:
        images_metadata: list of dicts containing image metadata
        extraction_radius_pix: (float) Used to calculate the 'skyregion' 
        dataset_id: dataset id to be used. don't use value from parset file
                    since this can be -1 (TraP way of setting auto increment)
    Returns:
        the database ID of this dataset
    """
    database = Database()
    dataset = DataSet(id=dataset_id, database=database)
    image_ids = []

    # sort images by timestamp
    images_metadata.sort(key=lambda m: m['taustart_ts'])

    for metadata in images_metadata:
        metadata['freq_bw_max'] = bandwidth_max
        metadata['xtr_radius'] = extraction_radius_pix * abs(metadata['deltax'])
        filename = metadata['url']
        db_image = Image(data=metadata, dataset=dataset)
        image_ids.append(db_image.id)
        logger.debug("stored %s with ID %s" % (os.path.basename(filename),
                                              db_image.id))
    return image_ids


def get_accessors(images):
    results = []
    for image in images:
        try:
            accessor = tkp.accessors.open(image)
        except TypeError as e:
            logger.error("Can't open image %s: %s" % (image, e))
            raise
        else:
            results.append(accessor)
    return results


def paths_to_fits(paths):
    """
    paths (list): list of paths to a astronomical image which can be opened with
                  casacore
                  
    returns:
        list: of HDUlist objects
    """
    for path in paths:
        try:
            i = casacore_image(path)
        except RuntimeError:
            logging.error("can't open image {}".format(path))
            yield
        else:
            with NamedTemporaryFile() as temp_file:
                i.tofits(temp_file.name)
                fits = fits_open(temp_file.name)
                yield cPickle.dumps(fits[0].data), str(fits[0].header)
