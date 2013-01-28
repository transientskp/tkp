from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from tkp.database.orm import Image
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import tkp.config
import trap.ingredients as ingred
from tkp.database.utils import general as dbgen


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

    def go(self):
        self.logger.info("Extracting sources...")
        super(source_extraction, self).go()

        image_ids = self.inputs['args']
        image_paths = [Image(id=id).url for id in image_ids]

        sources_sets = self.distributed(image_ids, image_paths)
        for (image_id, sources) in sources_sets:
            dbgen.insert_extracted_sources(image_id, sources, 'blind')

        if self.error.isSet():
            self.logger.warn("Failed source extraction process detected")
            return 1
        else:
            return 0

    def distributed(self, image_ids, image_paths):
        nodes = ingred.common.nodes_available(self.config)

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
                        tkp.config.CONFIGDIR
                    ]
                )
            )
        jobs = self._schedule_jobs(jobs)
        results = []
        for job in jobs.itervalues():
            if 'sources' in job.results:
                image_id = job.results['image_id']
                sources = job.results['sources']
                results.append((image_id, sources))
        return results

if __name__ == '__main__':
    sys.exit(source_extraction().main())
