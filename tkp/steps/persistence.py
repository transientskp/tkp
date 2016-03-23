"""
This `step` is used for the storing of images and metadata
to the database and image cache (mongodb).
"""
import os
import logging
import warnings
from tempfile import NamedTemporaryFile

from casacore.images import image as casacore_image

import tkp.accessors
from tkp.db.database import Database
from tkp.db.orm import DataSet, Image
from tkp.quality.statistics import rms_with_clipped_subregion


logger = logging.getLogger(__name__)

def image_to_mongodb(filename, hostname, port, db):
    """Copy a file into mongodb"""

    try:
        import pymongo
        import gridfs
    except ImportError:
        msg = "Could not import MongoDB modules"
        logger.error(msg)
        warnings.warn(msg)
        return False

    try:
        connection = pymongo.MongoClient(host=hostname, port=port)
        gfs = gridfs.GridFS(connection[db])
        if gfs.exists(filename=filename):
            logger.debug("File already in database")

        else:
            # This conversion should work whether the input file
            # is in FITS or CASA format.
            # temp_fits_file is removed automatically when closed.
            temp_fits_file = NamedTemporaryFile()
            i = casacore_image(filename)
            i.tofits(temp_fits_file.name)
            new_file = gfs.new_file(filename=filename)
            with open(temp_fits_file.name, "r") as f:
                new_file.write(f)
            new_file.close()
            logger.info("Saved local copy of %s on %s"\
                        % (os.path.basename(filename), hostname))
    except Exception, e:
        logger.exception("Failed to save image to MongoDB: {}".format(filename))
        return False

    finally:
        # Only clear up things which have been created
        if "connection" in locals():
            connection.close()
        if "temp_fits_file" in locals():
            temp_fits_file.close()

    return True


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


def extract_metadatas(images, rms_est_sigma, rms_est_fraction):
    """
    Extracts metadata and rms_qc values from the list of images.

    Args:
        images: list of image urls
        rms_est_sigma: used for RMS calculation, see `tkp.quality.statistics`
        rms_est_fraction: used for RMS calculation, see `tkp.quality.statistics`

    Returns:
        a list of metadata's. The metadata will be False if extraction failed.
    """
    results = []
    for image in images:
        logger.info("Extracting metadata from %s" % image)
        try:
            accessor = tkp.accessors.open(image)
        except TypeError as e:
            logging.error("Can't open image %s: %s" % (image, e))
            results.append(False)
        else:
            metadata = accessor.extract_metadata()
            metadata['rms_qc'] = rms_with_clipped_subregion(accessor.data,
                                                rms_est_sigma,rms_est_fraction)
            results.append(metadata)
    return results


def store_images(images_metadata, extraction_radius_pix, dataset_id):
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
        metadata['xtr_radius'] = extraction_radius_pix * abs(metadata['deltax'])
        filename = metadata['url']
        db_image = Image(data=metadata, dataset=dataset)
        image_ids.append(db_image.id)
        logger.info("stored %s with ID %s" % (os.path.basename(filename), db_image.id))
    return image_ids


def node_steps(images, image_cache_config, rms_est_sigma, rms_est_fraction):
    """
    this function executes all persistence steps that should be executed on a node.
    Note: Should only be used in a node recipe
    """
    mongohost = image_cache_config['mongo_host']
    mongoport = image_cache_config['mongo_port']
    mongodb = image_cache_config['mongo_db']
    copy_images = image_cache_config['copy_images']

    if copy_images:
        for image in images:
            image_to_mongodb(image, mongohost, mongoport, mongodb)
    else:
        logger.info("Not copying images to mongodb")

    metadatas = extract_metadatas(images, rms_est_sigma, rms_est_fraction)
    return metadatas
