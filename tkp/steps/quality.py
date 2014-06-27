"""
All generic quality checking routines.
"""
import logging

from tkp.telescope.lofar.quality import reject_check_lofar
from tkp.accessors.lofaraccessor import LofarAccessor
import tkp.accessors
import tkp.db.quality
import tkp.quality.brightsource
import tkp.quality


logger = logging.getLogger(__name__)


def reject_check(image_path, job_config):
    """ checks if an image passes the quality check. If not, a rejection
        tuple is returned.

    NOTE: should only be used on a NODE

    args:
        id: database ID of image. This is not used but kept as a reference for
            distributed computation!
        image_path: path to image
        parset_file: parset file location with quality check parameters
    Returns:
        (rejection ID, description) if rejected, else None
    """

    accessor = tkp.accessors.open(image_path)
    # Only run LOFAR-specific QC checks on LOFAR images.
    if isinstance(accessor, LofarAccessor):
        return reject_check_lofar(
            accessor, job_config['quality_lofar']
        )
    else:
        logger.warn(
            "Unrecognised telescope %s for file %s, no quality checks.",
            accessor.telescope, image_path
        )
        return None


def reject_image(image_id, reason, comment):
    """
    Adds a rejection for an image to the database

    NOTE: should only be used on a MASTER node
    """
    tkp.db.quality.reject(image_id, reason, comment)
