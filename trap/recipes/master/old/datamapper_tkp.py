#                                                         LOFAR IMAGING PIPELINE
#
#                                 Map subbands on storage nodes to compute nodes
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

import os.path
from itertools import cycle
from collections import defaultdict

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.group_data import store_data_map
import lofarpipe.support.lofaringredient as ingredient
import lofarpipe.support.utilities

class datamapper_tkp(BaseRecipe):
    """
    Parses a list of filenames and attempts to map them to appropriate compute
    nodes (ie, which can access the files) on the LOFAR CEP cluster. Mapping
    by filename in this way is fragile, but is the best we can do for now.

    **Arguments**
    A list of datafiles.
    
    """
    inputs = {
        'mapfile': ingredient.StringField(
            '--mapfile',
            help="Full path (including filename) of mapfile to produce (clobbered if exists)"
        ),
        'subcluster': ingredient.StringField(
            '--subcluster',
            default='',
            help="Explicitly specify the subcluster, if it can't be deduced from the filename"
        ),
    }

    outputs = {
        'mapfile': ingredient.FileField(
            help="Full path (including filename) of generated mapfile"
        )
    }

    def go(self):
        self.logger.info("Starting datamapper run")
        super(datamapper_tkp, self).go()

        #      We build lists of compute-nodes per cluster and data-per-cluster,
        #          then match them up to schedule jobs in a round-robin fashion.
        # ----------------------------------------------------------------------
        clusterdesc = ClusterDesc(self.config.get('cluster', "clusterdesc"))
        if clusterdesc.subclusters:
            available_nodes = dict(
                (cl.name, cycle(get_compute_nodes(cl)))
                for cl in clusterdesc.subclusters
            )
        else:
            available_nodes = {
                clusterdesc.name: cycle(get_compute_nodes(clusterdesc))
            }

        data = defaultdict(list)
        datamap = []
        for filename in self.inputs['args']:
            if self.inputs['subcluster']:
                subcluster = self.inputs['subcluster']
            else:
                subcluster = filename.split(os.path.sep)[2]
            try:
                host = available_nodes[subcluster].next()
            except KeyError, key:
                self.logger.error("%s is not a known cluster" % str(key))
                raise
            datamap.append((host, filename))
            data[host].append(filename)

        #                                 Dump the generated mapping to a parset
        # ----------------------------------------------------------------------
        #parset = Parset()
        #for host, filenames in data.iteritems():
        #    parset.addStringVector(host, filenames)
        #
        #parset.writeFile(self.inputs['mapfile'])
        lofarpipe.support.utilities.create_directory(
                 os.path.dirname(self.inputs['mapfile'])
                 )
        store_data_map(self.inputs['mapfile'], datamap)
        self.outputs['mapfile'] = self.inputs['mapfile']

        return 0

if __name__ == '__main__':
    sys.exit(datamapper().main())
