"""
check image quality
"""
import logging
from tkp.db.model import Rejectreason, Rejection

logger = logging.getLogger(__name__)

reject_reasons = {
    'rms': Rejectreason(id=0, description='RMS invalid'),
    'beam': Rejectreason(id=1, description='beam invalid'),
    'bright_source': Rejectreason(id=2, description='bright source near'),
    'tau_time': Rejectreason(id=3, description='tau_time invalid'),
    'nan': Rejectreason(id=4, description='contains NaN'),
    'flat': Rejectreason(id=5, description='data is flat'),
}


def sync_rejectreasons(session):
    """
    Check if rejectreasons are in sync. If not, insert as needed and commit.

    Args:
        session (sqlalchemy.orm.Session): Database session.
    """
    if session.query(Rejectreason).count() != len(reject_reasons):
        dbreason_id_rows = session.query(Rejectreason.id).all()
        dbreason_ids = [row[0] for row in dbreason_id_rows]
        for r in reject_reasons.values():
            if r.id not in dbreason_ids:
                logger.info("Added to database Rejectreason {}:'{}'".format(
                    r.id, r.description
                ))
                session.add(r)
        session.commit()


def reject(imageid, reason, comment, session):
    """
    Add a reject reason to the db for a given image.

    Args:
        imageid (int): The image ID of the image to reject
        reason (tkp.db.model.Rejectreason): Why is the image rejected
        comment (str): An optional comment with details about the reason
        session (sqlalchemy.orm.Session): Database session.
    """
    r = Rejection(image_id=imageid,
                  rejectreason_id=reason.id,
                  comment=comment,
                  )
    session.add(r)


def unreject(imageid, session):
    """
    Remove any rejections of a given imageid

    Args:
        imageid: The image ID
        session (sqlalchemy.orm.Session): Database session.
    """
    session.query(Rejection).filter(
        Rejection.image_id == imageid).delete()


def isrejected(imageid, session):
    """
    Find out if an image is rejected or not
    Args:
        imageid: The image ID
        session (sqlalchemy.orm.Session): Database session.
    Returns:
        list: Empty if not rejected, a list of strings formatted as
            '{description}: {comment}' if rejected.
    """
    image_rejections = session.query(Rejection).filter(
        Rejection.image_id == imageid).all()
    return ["{}: {}".format(ir.rejectreason.description, ir.comment)
            for ir in image_rejections]
