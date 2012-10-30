from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import tkp.config


class source_extraction(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Extract sources from a FITS image
    """

    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Source finder configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    outputs = {
        'image_ids': ingredient.ListField()
    }

    def go(self):
        self.logger.info("Extracting sources")
        super(source_extraction, self).go()
        images = self.inputs['args']
        print 'IMAGES =', images

        # Obtain available nodes
        clusterdesc = ClusterDesc(self.config.get('cluster', "clusterdesc"))
        if clusterdesc.subclusters:
            available_nodes = dict(
                (cl.name, itertools.cycle(get_compute_nodes(cl)))
                for cl in clusterdesc.subclusters
                )
        else:
            available_nodes = {
                clusterdesc.name: get_compute_nodes(clusterdesc)
                }
        nodes = list(itertools.chain(*available_nodes.values()))

        # Running this on nodes, in case we want to perform source extraction
        # on individual images that are still stored on the compute nodes
        # Note that for that option, we will need host <-> data mapping,
        # eg VDS files
        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for image in images:
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image,
                        self.inputs['parset'],
                        tkp.config.CONFIGDIR
                    ]
                )
            )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        self.outputs['image_ids'] = [job.results['image_id'] for job in jobs.itervalues()]

        # Check if we recorded a failing process before returning
        if self.error.isSet():
            self.logger.warn("Failed source extraction process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(source_extraction().main())
