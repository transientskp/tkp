import os
import logging
from lofarpipe.support.lofarexceptions import PipelineException
from tkp.database import DataBase, DataSet
import tkp.utility.accessors
from tkp.utility.accessors import dbimage_from_accessor
from contextlib import closing
from tempfile import NamedTemporaryFile
from pyrap.images import image as pyrap_image

logger = logging.getLogger(__name__)


def store_to_mongodb(filename, hostname, port, db):
    try:
        import pymongo
        import gridfs
    except ImportError:
        logger.error("Could not import MongoDB modules")
        return

    try:
        # This conversion should work whether the input file
        # is in FITS or CASA format.
        temp_fits_file = NamedTemporaryFile()
        i = pyrap_image(filename)
        i.tofits(temp_fits_file.name)
    except Exception, e:
        logger.error("Could not convert image to FITS: %s" % (str(e)))
        temp_fits_file.close()
        return

    try:
        connection = pymongo.Connection(host=hostname, port=port)
        gfs = gridfs.GridFS(connection[db])
        new_file = gfs.new_file(filename=filename)
        with open(temp_fits_file.name, "r") as f:
            new_file.write(f)
        new_file.close()
        connection.close()
    except Exception, e:
        logger.error("Could not store image to MongoDB: %s" % (str(e)))
    finally:
        temp_fits_file.close()


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

            accessor = tkp.utility.accessors.open(image)
            db_image = dbimage_from_accessor(dataset=dataset, image=accessor)
            logger.info("stored %s with ID %s" % (os.path.basename(image), db_image.id))

            if store_images:
                logger.info("saving local copy of %s" % os.path.basename(image))
                store_to_mongodb(image, mongo_host, mongo_port, mongo_db)

        return dataset.id
