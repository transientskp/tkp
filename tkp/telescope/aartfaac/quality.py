import logging
import tkp.db.quality as dbquality
from tkp.quality.nan import contains_nan

logger = logging.getLogger(__name__)


def reject_check_aartfaac(accessor):
    """
    Executes quality checks for any type of telescope

    args:
        accessor: tkp.db.accessor image accessor

    returns: A rejection reason if the image is bad, None otherwise

    """
    nan_check = contains_nan(accessor.data)
    if nan_check:
        logger.warning("image %s REJECTED: contains NaN" % accessor.url)
        return dbquality.reject_reasons['nan'], ""
    else:
        return None
