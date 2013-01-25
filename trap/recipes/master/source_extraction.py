from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import tkp.config
import trap.ingredients as ingred


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
    }

    outputs = {
        'images_detections': ingredient.ListField(),
        'transients': ingredient.ListField()
    }

    def go(self):
        self.logger.info("Extracting sources...")
        super(source_extraction, self).go()
        image_ids = self.inputs['args']
        images_detections = self.distributed(image_ids)
        self.outputs['images_detections'] = images_detections
        # Just in case no sources were extracted or every image is rejected.
        self.outputs['transients'] = []

        if self.error.isSet():
            self.logger.warn("Failed source extraction process detected")
            return 1
        else:
            return 0

    def distributed(self, images_qualified):
        nodes = ingred.common.nodes_available(self.config)

        # Running this on nodes, in case we want to perform source extraction
        # on individual images that are still stored on the compute nodes
        # Note that for that option, we will need host <-> data mapping,
        # eg VDS files
        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for image_qualified in images_qualified:
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image_qualified,
                        self.inputs['parset'],
                        tkp.config.CONFIGDIR
                    ]
                )
            )
        jobs = self._schedule_jobs(jobs)
        images_detections = []
        for job in jobs.itervalues():
            if 'images_detections' in job.results:
                images_detections.append(job.results['images_detections'])
        return images_detections

if __name__ == '__main__':
    sys.exit(source_extraction().main())
