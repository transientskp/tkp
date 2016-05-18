import numpy as np
import logging
import tkp.db.quality as dbquality
logger = logging.getLogger(__name__)


def reject_check_generic_data(accessor):
    """
    Args:
        accessor: tkp.db.accessor image accessor

    Returns: A rejection reason if the image is bad, None otherwise
    """
    flat = reject_check_flat_data(accessor)
    if flat:
        return flat
    return None


def reject_check_flat_data(accessor):
    """
    Checks if an image is flat (i.e. a uniform value throughout).

    Flat implies bad data, since we always expect to see noise
     even if no sources are present.

    Args:
        accessor: tkp.db.accessor image accessor

    Returns: A rejection reason if the image is bad, None otherwise
    """
    data = accessor.data

    if np.ma.min(data)==np.ma.max(data):
        logger.warning("image %s REJECTED: image data is flat" % accessor.url)
        return dbquality.reject_reasons['flat'], ""
    else:
        return None