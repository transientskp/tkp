from __future__ import with_statement
from __future__ import division


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2011, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2011-11-09'



import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import tkp.database as tkpdb
import trap.ingredients as ingred

class monitoringlist(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Update the monitoring list with newly found transients.
    Transients that are already in the monitoring list will get
    their position updated from the runningcatalog.

    Args:
        dataset_id  --- id for the dataset to process.
    """

    inputs = {
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Source finder configuration parset (used to pull detection threshold)"
        ),
    }
    outputs = {
        'null_detections': ingredients.ListField()
    }

    def go(self):
        super(monitoringlist, self).go()
        image_id = self.inputs['args']
        image = self.inputs['args']
        null_detections = dbmon.get_nulldetections(image_id)
        if len(null_detections) != 0:
            forced_fits = self.distributed(null_detections, image)
            tuple_nd = [forced_fit.serialize() for forced_fit in forced_fits]
            dbgen.insert_extracted_sources(image_id, tuple_nd, 'ff_nd')
        
        if self.error.isSet():
            self.logger.warn("Failed monitoringlist process detected")
            return 1
        else:
            return 0

    def distributed(self, images):
        nodes = ingred.common.nodes_available(self.config)
        
        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for image_id in image_ids:
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                            image,
                        ]
                    )
                )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        forced_fits = []
        for job in jobs.itervalues():
            if 'forced_fits' in job.results:
                forced_fits += job.results['forced_fits']
        return forced_fits

if __name__ == '__main__':
    sys.exit(monitoringlist().main())
