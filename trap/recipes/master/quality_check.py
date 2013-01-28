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
from lofarpipe.support.remotecommand import ComputeJob
from tkp.database.orm import Image
import trap.ingredients as ingred


class quality_check(BaseRecipe, RemoteCommandRecipeMixIn):
    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Quality check configuration parset"
        ),
    }

    outputs = {
        'good_image_ids': ingredient.ListField()
    }


    def go(self):
        self.logger.info("Performing quality checks")
        super(quality_check, self).go()
        image_ids = self.inputs['args']
        ids_urls = [(id, Image(id=id).url) for id in image_ids]
        rejected_images = self.distributed(ids_urls)
        for rejected_image in rejected_images:
                (image_id, reason, comment) = rejected_image
                ingred.quality.reject_image(image_id, reason, comment)

        rejected_ids = [i[0] for i in rejected_images]
        good_image_ids = [i for i in image_ids if i not in rejected_ids]
        self.outputs['good_image_ids'] = good_image_ids

        if self.error.isSet():
            self.logger.error("Failed quality control process detected")
            return 1
        else:
            return 0


    def distributed(self, ids_urls):
        nodes = ingred.common.nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for (id, url) in ids_urls:
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
        
        jobs = self._schedule_jobs(jobs)
        images_qualified = []
        for job in jobs.itervalues():
                rejected = job.results.get('rejected', None)
                if rejected:
                    images_qualified.append(job.results['rejected'])
        return images_qualified

