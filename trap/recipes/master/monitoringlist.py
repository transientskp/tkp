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
from lofar.parameterset import parameterset

import tkp.database as tkpdb

import tkp.config


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
        ds_id = self.inputs['args'][0]
        # Get image_ids and their file names
        with closing(tkpdb.DataBase()) as database:
            dataset = tkpdb.DataSet(database=database, id = ds_id)
            dataset.update_images()
            image_ids = [img.id for img in dataset.images]
            ids_filenames = tkpdb.utils.get_imagefiles_for_ids(
                database.connection, image_ids)
            
            #Mark sources which need monitoring
            detection_thresh = parameterset(self.inputs['parset']).getFloat('detection.threshold', 5)
            dataset.mark_transient_candidates(single_epoch_threshold = detection_thresh,
                                              combined_threshold = detection_thresh)
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
                        dataset.id,
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
