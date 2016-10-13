"""
Code for storing FITS images in the database
"""
from tkp.db import Database
from tkp.db.model import ImageData
import logging
from sqlalchemy.sql.expression import bindparam
from sqlalchemy import insert


logger = logging.getLogger(__name__)


def store_fits(db_images, fits_datas, fits_headers):
    """
    bulk store fits data in database

    args:
        db_images (list): list of ``tkp.db.model.Image``s
        fits_datas (list): list of serialised numpy arrays
        fits_headers (list): list of serialised fits headers (string)
    """
    values = [{'image': i.id, 'fits_data': d, 'fits_header': h} for i, d, h in
              zip(db_images, fits_datas, fits_headers)]
    stmt = insert(ImageData).values(
        {
            'image': bindparam('image'),
            'fits_data': bindparam('fits_data'),
            'fits_header': bindparam('fits_header'),
        }
    )

    db = Database()
    db.session.execute(stmt, values)
    db.session.commit()

