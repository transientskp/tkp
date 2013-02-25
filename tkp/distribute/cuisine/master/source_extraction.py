from __future__ import with_statement
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.remotecommand import ComputeJob
from tkp.database.orm import Image
from tkp.distribute.cuisine.common import TrapMaster, nodes_available


class source_extraction(TrapMaster):
    """Extract sources from a FITS image"""

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
        'sources_sets': ingredient.ListField()
    }

    def trapstep(self):
        self.logger.info("Extracting sources...")
        image_ids = self.inputs['args']
        image_paths = [Image(id=id).url for id in image_ids]

        sources_sets = self.distributed(image_ids, image_paths)
        self.outputs['sources_sets'] = sources_sets

    def distributed(self, image_ids, image_paths):
        nodes = nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for id, url in zip(image_ids, image_paths):
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        id,
                        url,
                        self.inputs['parset'],
                    ]
                )
            )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        results = []
        for job in jobs.itervalues():
            if 'sources' in job.results:
                image_id = job.results['image_id']
                sources = job.results['sources']
                results.append((image_id, sources))
            else:
                self.error.set()
        return results

