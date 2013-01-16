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
import trap.ingredients.monitoringlist
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

    def go(self):
        super(monitoringlist, self).go()
        dataset_id = self.inputs['args'][0]
        database = tkpdb.DataBase()
        dataset = tkpdb.DataSet(database=database, id=dataset_id)

        dataset.update_images()
        image_ids = [img.id for img in dataset.images if not img.rejected]
        trap.ingredients.monitoringlist.mark_sources(dataset_id, self.inputs['parset'])

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
                            image_id,
                        ]
                    )
                )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        # Check if we recorded a failing process before returning
        if self.error.isSet():
            self.logger.warn("Failed monitoringlist process detected")
            return 1
        return 0


if __name__ == '__main__':
    sys.exit(monitoringlist().main())
