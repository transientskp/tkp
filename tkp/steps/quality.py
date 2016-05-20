"""
All generic quality checking routines.
"""
import logging
import tkp.db.quality
import tkp.quality
import tkp.quality.brightsource
from tkp.accessors import AartfaacCasaImage
from tkp.accessors.lofaraccessor import LofarAccessor
from tkp.db import Database
from tkp.telescope.aartfaac.quality import reject_check_aartfaac
from tkp.telescope.generic.quality import reject_check_generic_data
from tkp.telescope.lofar.quality import reject_check_lofar


logger = logging.getLogger(__name__)


def reject_check(image_path, job_config):
    """
    Check if an image passes the quality checks.

    If not, a rejection reason is returned.

    args:
        id: database ID of image. This is not used but kept as a reference for
            distributed computation!
        image_path: path to image
        parset_file: parset file location with quality check parameters
    Returns:
        (rejection ID, description) if rejected, else None
    """

    accessor = tkp.accessors.open(image_path)

    rejected = reject_check_generic_data(accessor)
    if rejected:
        return rejected

    if isinstance(accessor, AartfaacCasaImage):
        rejected = reject_check_aartfaac(accessor)
        if rejected:
            return rejected

    # Only run LOFAR-specific QC checks on LOFAR images.
    if isinstance(accessor, LofarAccessor):
        rejected = reject_check_lofar(accessor, job_config)
        if rejected:
            return rejected
    else:
        msg = "no specific quality checks for " + accessor.telescope
        logger.warn(msg)


def reject_image(image_id, reason, comment):
    """
    Adds a rejection for an image to the database
    """
    session = Database().Session()
    tkp.db.quality.reject(image_id, reason, comment,session)
    session.commit()
