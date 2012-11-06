import os
import os.path
import logging
from lofarpipe.support.lofarexceptions import PipelineException
from tkp.database import DataBase, DataSet
from tkp.utility.accessors import FITSImage
from tkp.utility.accessors import dbimage_from_accessor
from contextlib import closing

logger = logging.getLogger(__name__)


def store_to_mongodb(filename, hostname, port, db):
    try:
        import pymongo
        import gridfs
    except ImportError:
        logger.error("Could not import MongoDB modules")
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
        logger.error("Could not store image to MongoDB: %s" % (str(e)))


def store(images, description, dataset_id=-1, store_images=False, mongo_host="localhost", mongo_port=27017, mongo_db="trap"):
    """ Add dataset to database, optionally create copy of images
    Args:
        images: list of file paths pointing to image files
        description: describes this dataset
    Returns:
        the database ID of this dataset
    """
    with closing(DataBase()) as database:
        if dataset_id == -1:
            dataset = DataSet({'description': description}, database)
        else:
            dataset = DataSet(id=dataset_id, database=database)

        for image in images:
            if not os.path.exists(image):
                message = "Image '%s' not found" % image
                logger.error(message)
                raise PipelineException(message)

            fitsimage = FITSImage(image)
            db_image = dbimage_from_accessor(dataset=dataset, image=fitsimage)
            logger.info("stored %s with ID %s" % (os.path.basename(image), db_image.id))

            if store_images:
                logger.info("saving local copy of %s" % os.path.basename(image))
                store_to_mongodb(image, mongo_host, mongo_port, mongo_db)

        return dataset.id