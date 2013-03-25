from __future__ import with_statement
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.remotecommand import ComputeJob
from tkp.steps.persistence import master_steps
from tkp.distribute.cuisine.common import TrapMaster, nodes_available


class persistence(TrapMaster):
    """Store an image into the database"""

    inputs = {
      'extraction_radius_pix': ingredient.FloatField(
            '--extraction_radius_pix',
            dest='extraction_radius_pix',
            help="Source extraction radius (in pixels)"
        ),
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="persistence configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }
    outputs = {
        'dataset_id': ingredient.IntField()
    }

    def trapstep(self):
        images = self.inputs['args']
        metadatas = self.distributed(images)
        dataset_id, image_ids = master_steps(metadatas,
                                             self.inputs['extraction_radius_pix'],
                                             self.inputs['parset'])
        self.outputs['dataset_id'] = dataset_id

    def distributed(self, images):
        nodes = nodes_available(self.config)

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
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        metadatas = []
        for job in jobs.itervalues():
            if 'metadatas' in job.results:
                metadatas += job.results['metadatas']
            else:
                self.error.set()
        return metadatas

