import sys
import logging
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class TrapNode(LOFARnodeTCP):
    """
    This class should be inherited to create a Trap Node recipe. The
    trapstep method should be used from implementing your recipe node logic.
    """
    def run(self, *args, **kwargs):
        with log_time(self.logger):
            # capture all logging and sent it to the master
            logdrain = logging.getLogger()
            logdrain.level = self.logger.level
            logdrain.handlers = self.logger.handlers
            self.logger.handlers = []
            try:
                self.trapstep(*args, **kwargs)
            except Exception,e:
                self.logger.error(e)
                return 1
        return 0

    def trapstep(self):
        raise NotImplementedError()


def node_run(name, nodeclass):
    """this function should be called from every Trap Node Recipe so it can
    be called on a node.
    """
    if name == "__main__":
        jobid, jobhost, jobport = sys.argv[1:4]
        sys.exit(nodeclass(jobid, jobhost, jobport).run_with_stored_arguments())