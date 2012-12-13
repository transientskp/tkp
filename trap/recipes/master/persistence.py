from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob
from trap.ingredients.persistence import master_steps


class persistence(BaseRecipe, RemoteCommandRecipeMixIn):
    """Store an image into the database"""

    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="persistence configuration parset"
        ),
    }
    outputs = {
        'dataset_id': ingredient.IntField()
    }

    def go(self):
        super(persistence, self).go()
        images = self.inputs['args']
        metadatas = self.distributed(images)
        dataset_id, image_ids = master_steps(metadatas, self.inputs['parset'])
        self.outputs['dataset_id'] = dataset_id

        if self.error.isSet():
            self.logger.warn("Failed persistence process detected")
            return 1
        else:
            return 0

    def distributed(self, images):
        clusterdesc = ClusterDesc(self.config.get('cluster', "clusterdesc"))
        if clusterdesc.subclusters:
            available_nodes = dict(
                (cl.name, itertools.cycle(get_compute_nodes(cl)))
                    for cl in clusterdesc.subclusters
            )
        else:
            available_nodes = {clusterdesc.name: get_compute_nodes(clusterdesc)}
        nodes = list(itertools.chain(*available_nodes.values()))

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
                    ]
                )
            )
        # TODO: need to find a good way to set the max_per_node
        jobs = self._schedule_jobs(jobs, max_per_node=4)
        metadatas = []
        for job in jobs.itervalues():
            if 'metadatas' in job.results:
                metadatas += job.results['metadatas']
        return metadatas

if __name__ == '__main__':
    sys.exit(persistence().main())
