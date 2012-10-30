import os
import logging
from lofarpipe.support.lofarexceptions import PipelineException
from lofarpipe.support.utilities import log_time
from tkp.database import DataBase, DataSet
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import dbimage_from_accessor

logger = logging.getLogger(__name__)

def store_to_mongodb(filename, hostname, port, db):
    try:
        import pymongo
        import gridfs
    except ImportError:
        logger.warn("Could not import MongoDB modules")
        return

    try:
        connection = pymongo.Connection(host=hostname, port=port)
        gfs = gridfs.GridFS(connection[db])
        new_file = gfs.new_file(filename=filename)
        with open(filename, "r") as f:
            new_file.write(f)
        new_file.close()
        connection.close()
    except Exception, e:
        logger.warn("Could not store image to MongoDB: %s" % (str(e)))


def store(images, description, store_images=False, mongo_host="localhost", mongo_port=27017, mongo_db="trap"):
    """ Add dataset to database, optionally create copy of images
    Args:
        images: list of file paths pointing to image files
        description: describes this dataset
    Returns:
        the database ID of this dataset
    """
    log_time(logger)

    database = DataBase()
    dataset = DataSet({'description': description}, database)

    for image in images:
        if not os.path.exists(image):
            message = "Image '%s' not found" % image
            logger.error(message)
            raise PipelineException(message)

        logging.info("storing %s in the database" % image)
        fitsimage = FITSImage(image)
        db_image = dbimage_from_accessor(dataset=dataset, image=fitsimage)

        if store_images:
            logging.info("saving local copy of %s" % image)
            store_to_mongodb(image, mongo_host, mongo_port, mongo_db, logger)

    return dataset.id