"""
Code for storing FITS images in the database
"""
from sqlalchemy import update
from tkp.db.model import Image
import logging
import cPickle

logger = logging.getLogger(__name__)


def store_fits(images, fits_datas, fits_headers):
    """
    Store an image in the database. assumes the ID already exists.

    ids (list): list of database ID's
    paths (list): a list of image paths or fits objects
    """
    for image, data, header in zip(images, fits_datas, fits_headers):
        yield update(Image).\
            where(Image.id == image.id).\
            values(fits_data=cPickle.dumps(data), fits_header=header)
