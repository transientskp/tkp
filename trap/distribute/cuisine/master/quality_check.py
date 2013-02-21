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
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.remotecommand import ComputeJob
from tkp.database.orm import Image
import trap.ingredients as ingred
from trap.distribute.cuisine.common import TrapMaster, nodes_available


class quality_check(TrapMaster):
    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Quality check configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    outputs = {
        'good_image_ids': ingredient.ListField()
    }

    def trapstep(self):
        self.logger.info("Performing quality checks")
        image_ids = self.inputs['args']
        urls = [Image(id=id).url for id in image_ids]
        rejected_images = self.distributed(image_ids, urls)
        for image_id, (reason, comment) in rejected_images:
                ingred.quality.reject_image(image_id, reason, comment)

        rejected_ids = [i[0] for i in rejected_images]
        good_image_ids = [i for i in image_ids if i not in rejected_ids]
        self.outputs['good_image_ids'] = good_image_ids


    def distributed(self, image_ids, image_urls):
        nodes = nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for image_id, image_url in zip(image_ids, image_urls):
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image_id,
                        image_url,
                        self.inputs['parset'],
                    ]
                )
            )
        
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        images_qualified = []
        for job in jobs.itervalues():
                rejected = job.results.get('rejected', None)
                if rejected:
                    image_id = job.results['image_id']
                    images_qualified.append((image_id, rejected))
        return images_qualified

