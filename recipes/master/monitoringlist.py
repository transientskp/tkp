from __future__ import with_statement
from __future__ import division


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2011, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2011-11-09'



import sys
import os
from contextlib import closing
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn

import tkp.database.database
import tkp.database.dataset
import tkp.database.utils as dbu
from tkp.classification.transient import Transient
from tkp.classification.transient import Position
from tkp.classification.transient import DateTime
from tkp.database.database import DataBase
from tkp.database.dataset import DataSet


class monitoringlist(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Update the monitoring list with newly found transients.
    Transients that are already in the monitoring list will get
    their position updated from the runningcatalog.
    """
    
    inputs = {
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
        }
    
    def go(self):
        super(monitoringlist, self).go()
        # Get image_ids and their file names
        image_ids = self.inputs['args']
        with closing(DataBase()) as database:
            ids_filenames = dbu.get_imagefiles_for_ids(
                database.connection, image_ids)
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
        for image_id, filename in ids_filenames:
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        filename,
                        image_id,
                        tkp.config.CONFIGDIR
                        ]
                    )
                )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        
        #                Check if we recorded a failing process before returning
        # ----------------------------------------------------------------------
        if self.error.isSet():
            self.logger.warn("Failed monitoringlist process detected")
            return 1
        return 0


if __name__ == '__main__':
    sys.exit(transient_search().main())
