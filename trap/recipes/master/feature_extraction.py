import sys
import itertools
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support import lofaringredient
import trap.ingredients as ingred

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
        nodes = ingred.common.nodes_available(self.config)
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
