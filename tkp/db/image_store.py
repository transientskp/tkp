"""
Code for storing FITS images in the database
"""
from tkp.db import Database
from tkp.db.model import Image
import logging
from sqlalchemy.sql.expression import bindparam
from sqlalchemy import update


logger = logging.getLogger(__name__)


def store_fits(db_images, fits_datas, fits_headers):
    """
    bulk store fits data in database

    args:
        db_images (list): list of ``tkp.db.model.Image``s
        fits_datas (list): list of serialised numpy arrays
        fits_headers (list): list of serialised fits headers (string)
    """
    values = [{'_id': i.id, 'fits_data': d, 'fits_header': h} for i, d, h in
              zip(db_images, fits_datas, fits_headers)]

    stmt = update(Image).where(Image.id == bindparam('_id')). \
        values({'fits_data': bindparam('fits_data'),
                'fits_header': bindparam('fits_header'),
                })

    db = Database()
    db.session.execute(stmt, values)
    db.session.commit()

