from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.parset import parameterset
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from tkp.database.utils import monitoringlist as dbmon
from tkp.database.utils import general as dbgen
import trap.ingredients as ingred
from tkp.database.orm import Image


class mon_detections(BaseRecipe, RemoteCommandRecipeMixIn):
    """Get the monitoring sources that weren't found by the sourcefinder nor 
    were added as null detections to extractedsource. Do a forced fit
    at the positions and append the results to extractedsources into the database"""
    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="persistence configuration parset"
        ),
    }

    def go(self):
        super(mon_detections, self).go()
        parset_file = self.inputs['parset']
        parset = parameterset(parset_file)
        deRuiter_radius = parset.getFloat('deRuiter_radius', 3.717)

        image_ids = self.inputs['args']
        image_paths = [Image(id=id).url for id in image_ids]

        self.logger.info("starting mon_detections for images %s" % image_ids)

        image_nds = [dbmon.get_nulldetections(image_id, deRuiter_radius) for image_id in image_ids]
        ff_mds = self.distributed(image_ids, image_paths, image_nds)

        for image_id, ff_md in ff_mds:
            dbgen.insert_extracted_sources(image_id, ff_md, 'ff_mon')

        if self.error.isSet():
            self.logger.warn("Failed mon_detections process detected")
            return 1
        else:
            return 0

    def distributed(self, image_ids, image_paths, image_nds):
        nodes = ingred.common.nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        host = hosts.next()
        for image_id, image_path, image_nd in zip(image_ids, image_paths, image_nds):
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image_id,
                        image_path,
                        image_nd,
                    ]
                )
            )

        jobs = self._schedule_jobs(jobs)
        results = []
        for job in jobs.itervalues():
                if 'ff_mon' in job.results:
                    ff_mon = job.results['ff_mon']
                    image_id = job.results['image_id']
                    results.append((image_id, ff_mon))
        return results

if __name__ == '__main__':
    sys.exit(mon_detections().main())
