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


class null_detections(BaseRecipe, RemoteCommandRecipeMixIn):
    """Get the null detections in an image, do a forced fit and 
    append the results to extractedsources into the database"""

    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="null_detection configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    def go(self):
        super(null_detections, self).go()
        parset_file = self.inputs['parset']
        
        image_detections = self.inputs['args'][0]
        image = image_detections['image_qualified']['image']
        good_image = image_detections['image_qualified']['good_image']
        image_id = self.inputs['args'][1]
        
        if good_image:
            parset = parameterset(parset_file)
            deRuiter_radius = parset.getFloat('deRuiter_radius', 3.717)
            nd = dbmon.get_nulldetections(image_id, deRuiter_radius)
        
            ff_nd = self.distributed(image, nd, parset_file)
            forced_fits = ff_nd[0]['forced_fits']
            dbgen.insert_extracted_sources(image_id, forced_fits, 'ff_nd')

        if self.error.isSet():
            self.logger.warn("Failed null_detections process detected")
            return 1
        else:
            return 0

    def distributed(self, image, nd, parset_file):
        nodes = ingred.common.nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        host = hosts.next()
        jobs.append(
            ComputeJob(
                host, command,
                arguments=[
                    image,
                    nd,
                    parset_file,
                ]
            )
        )

        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        ff_nd = []
        for job in jobs.itervalues():
                if 'ff_nd' in job.results:
                    ff_nd.append(job.results['ff_nd'])
        return ff_nd

if __name__ == '__main__':
    sys.exit(null_detections().main())
