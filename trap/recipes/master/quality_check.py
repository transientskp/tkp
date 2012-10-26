"""
This recipe will perform some basic quality checks on a given image.

For now it:
    * Checks if the RMS value of an image is within a acceptable range,
    * More to come.

If an image passes theses tests, the image id will be put in the image_ids
output variable, otherwise an rejection entry with put in the rejection
database table.
"""

import itertools
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob

class quality_check(BaseRecipe, RemoteCommandRecipeMixIn):
    inputs = {
        'dataset_id': ingredient.IntField(
            '--dataset-id',
            help='Dataset to which images belong',
            default=None
        ),
    }
    outputs = {
        'image_ids': ingredient.ListField()
    }


    def go(self):
        self.logger.info("Performing quality checks")
        super(quality_check, self).go()
        images = self.inputs['args']
        print 'IMAGES =', images
        dataset_id = self.inputs['dataset_id']

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
                        dataset_id,
                    ]
                )
            )
        jobs = self._schedule_jobs(jobs)
        self.outputs['image_ids'] = [job.results['image_id'] for job in jobs.itervalues()]

        if self.error.isSet():
            self.logger.warn("Failed quality control process detected")
            return 1
        else:
            return 0