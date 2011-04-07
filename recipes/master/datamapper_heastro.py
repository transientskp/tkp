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
from lofarpipe.support.parset import Parset
import lofarpipe.support.lofaringredient as ingredient


class datamapper_heastro(BaseRecipe):

    inputs = {
        'mapfile': ingredient.StringField(
            '--mapfile',
            help="Filename for output mapfile (clobbered if exists)"
        )
    }

    outputs = {
        'mapfile': ingredient.FileField()
    }

    def go(self):
        self.logger.info("Starting datamapper run")
        super(datamapper_heastro, self).go()

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
        subcluster = 'heastro'
        for filename in self.inputs['args']:
            try:
                host = available_nodes[subcluster].next()
            except KeyError, key:
                self.logger.error("%s is not a known cluster" % str(key))
                raise

            data[host].append(filename)

        #                                 Dump the generated mapping to a parset
        # ----------------------------------------------------------------------
        parset = Parset()
        for host, filenames in data.iteritems():
            parset.addStringVector(host, filenames)

        parset.writeFile(self.inputs['mapfile'])
        self.outputs['mapfile'] = self.inputs['mapfile']

        return 0

if __name__ == '__main__':
    sys.exit(datamapper_heastro().main())
