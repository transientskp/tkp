"""Subroutines / ingredients which are not specific to any particular recipe"""
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
import itertools

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
