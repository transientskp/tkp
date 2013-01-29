"""Subroutines / ingredients which are not specific to any particular recipe

TODO: This is implementation specific and should be moved outside this module.

"""
import logging
import sys
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
import itertools
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.pipelinelogging import log_time

def nodes_available(config):
    """ Obtain list of available nodes """
    clusterdesc = ClusterDesc(config.get('cluster', "clusterdesc"))
    if clusterdesc.subclusters:
        available_nodes = dict(
            (cl.name, itertools.cycle(get_compute_nodes(cl)))
            for cl in clusterdesc.subclusters
            )
    else:
        available_nodes = {
            clusterdesc.name: get_compute_nodes(clusterdesc)
            }
    return list(itertools.chain(*available_nodes.values()))


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
            #self.logger = logdrain

            try:
                self.trapstep(*args, **kwargs)
            except Exception,e:
                self.logger.error(e)
                return 1
        return 0

    def trapstep(self):
        raise NotImplementedError()


class TrapMaster(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    This class should be inherited to create a Trap Master recipe. The
    trapstep method should be used from implementing your recipe node logic.
    """
    def go(self, *args, **kwargs):
        super(TrapMaster, self).go()
        # call the actual do-er
        self.trapstep(*args, **kwargs)
        if self.error.isSet():
            self.logger.warn("Failed null_detections process detected")
            return 1
        else:
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