import logging
import tkp.db
import tkp.quality
from tkp.quality.nan import contains_nan

logger = logging.getLogger(__name__)


def reject_check_generic(accessor):
    """
    Executes quality checks for any type of telescope

    args:
        accessor: tkp.db.accessor image accessor

    returns: A rejection reason if the image is bad, None otherwise

    """
    nan_check = contains_nan(accessor.data)
    if nan_check:
        logger.warning("image %s REJECTED: contains NaN" % accessor.url)
        return tkp.db.quality.reason['nan'].id, ""
    else:
        return None
