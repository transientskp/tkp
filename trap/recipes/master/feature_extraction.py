import sys
import itertools
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support import lofaringredient

class feature_extraction(BaseRecipe, RemoteCommandRecipeMixIn):

    inputs = dict(
        nproc=lofaringredient.IntField(
            '--nproc',
            default=8,
            help="Maximum number of simultaneous processes per output node"),
        )
    outputs = dict(
        transients=lofaringredient.ListField()
        )

    def go(self):
        super(feature_extraction, self).go()
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
        self.logger.info("available nodes = %s" % str(available_nodes))    

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        nodes = itertools.cycle(nodes)
        for transient in self.inputs['args']:
            node = nodes.next()
            jobs.append(
                ComputeJob(
                    node,
                    command,
                    arguments=[
                        transient,
                        ]
                    )
                )
        self.logger.info("Scheduling jobs")
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        self.logger.info("Getting Transient objects")
        self.outputs['transients'] = [job.results['transient'] for job in jobs.itervalues()]
                        
        if self.error.isSet():
            return 1
        else:
            return 0


if __name__ == '__main__':
    sys.exit(feature_extraction().main())
