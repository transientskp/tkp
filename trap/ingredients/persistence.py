
import os
import logging
import warnings
from lofarpipe.support.parset import parameterset
import tkp.utility.accessors
from tkp.database import DataBase, DataSet, Image
from tkp.utility.accessors.dataaccessor import extract_metadata
from tempfile import NamedTemporaryFile
from pyrap.images import image as pyrap_image

logger = logging.getLogger(__name__)


def parse_parset(parset_file):
    """parse a persistence recipe specific parset file
    """
    parset = parameterset(parset_file)
    result = {}
    result['description'] = parset.getString('description', 'TRAP dataset')
    result['dataset_id'] = parset.getInt('dataset_id', -1)
    result['copy_images'] = parset.getBool('copy_images', False)
    result['mongo_host'] = parset.getString('mongo_host', 'localhost')
    result['mongo_port'] = parset.getInt('mongo_port', 27017)
    result['mongo_db'] = parset.getString('mongo_db', 'tkp')
    return result


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
        connection = pymongo.Connection(host=hostname, port=port)
        gfs = gridfs.GridFS(connection[db])
        if gfs.exists(filename=filename):
            logger.debug("File already in database")

        else:
            # This conversion should work whether the input file
            # is in FITS or CASA format.
            # temp_fits_file is removed automatically when closed.
            temp_fits_file = NamedTemporaryFile()
            i = pyrap_image(filename)
            i.tofits(temp_fits_file.name)
            new_file = gfs.new_file(filename=filename)
            with open(temp_fits_file.name, "r") as f:
                new_file.write(f)
            new_file.close()
            logger.info("Saved local copy of %s on %s"\
                        % (os.path.basename(filename), hostname))
    except Exception, e:
        msg = "Failed to save image to MongoDB: %s" % (str(e),)
        logger.error(msg)
        warnings.warn(msg)
        return False

    finally:
        connection.close()

        # Only close this if it has been created.
        if "temp_fits_file" in locals():
            temp_fits_file.close()

    return True


def create_dataset(dataset_id, description):
    """ Creates a dataset if it doesn't exists
    Note: Should only be used in a master recipe
    Returns:
      the database ID of this dataset
    """
    database = DataBase()
    if dataset_id == -1:
        dataset = DataSet({'description': description}, database)
    else:
        dataset = DataSet(id=dataset_id, database=database)
    return dataset.id


def extract_metadatas(images):
    results = []
    for image in images:
        logger.info("Extracting metadata from %s" % image)
        accessor = tkp.utility.accessors.open(image)
        results.append(extract_metadata(accessor))
    return results


def store_images(images_metadata, dataset_id):
    """ Add images to database.
    Note that all images in one dataset should be inserted in one go, since the
    order is very important here. If you don't add them all in once, you should
    make sure they are added in the correct order e.g. sorted by observation
    time.

    Note: Should only be used in a master recipe

    Args:
        images_metadata: list of dicts containing image metadata
        dataset_id: dataset id to be used. don't use value from parset file
                    since this can be -1 (trap way of setting auto increment)
    Returns:
        the database ID of this dataset
    """
    database = DataBase()
    dataset = DataSet(id=dataset_id, database=database)
    image_ids = []

    # sort images by timestamp
    images_metadata.sort(key=lambda m: m['taustart_ts'])

    for metadata in images_metadata:
        filename = metadata['url']
        db_image = Image(data=metadata, dataset=dataset)
        image_ids.append(db_image.id)
        logger.info("stored %s with ID %s" % (os.path.basename(filename), db_image.id))
    return image_ids


def node_steps(images, parset_file):
    """
    this function executes all persistence steps that should be executed on a node.
    Note: Should only be used in a node recipe
    """
    persistence_parset = parse_parset(parset_file)
    mongohost = persistence_parset['mongo_host']
    mongoport = persistence_parset['mongo_port']
    mongodb = persistence_parset['mongo_db']
    copy_images = persistence_parset['copy_images']

    if copy_images:
        for image in images:
            image_to_mongodb(image, mongohost, mongoport, mongodb)
    else:
        logger.info("Not copying images to mongodb")

    metadatas = extract_metadatas(images)
    return metadatas


def master_steps(metadatas, parset_file):
    """this function executes all persistence steps that should be executed on
        a master.
    Args:
        parset_file: path to a parset file containig persistence settings
        metadatas: a list of dicts containing info from Image Accessors. This
                   is returned by the node recipe
    """
    persistence_parset = parse_parset(parset_file)
    logger.info("creating dataset in database ...")
    dataset_id = create_dataset(
        persistence_parset['dataset_id'],
        persistence_parset['description'])
    logger.info("added dataset with ID %s" % dataset_id)

    logger.info("Storing images")
    image_ids = store_images(metadatas, dataset_id)
    return dataset_id, image_ids


def all(images, parset_file):
    """
    execute node and then master code, should be used in local run only!
    """
    metadatas = node_steps(images, parset_file)
    return master_steps(metadatas, parset_file)
