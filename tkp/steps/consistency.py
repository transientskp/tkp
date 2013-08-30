import logging
import tkp.db.consistency

logger = logging.getLogger(__name__)


def master_steps():
    """This function executes the consistency step that should be executed on
    a master.
    """
    consistent = tkp.db.consistency.check()
