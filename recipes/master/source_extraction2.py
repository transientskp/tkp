from __future__ import with_statement
from contextlib import contextmanager

import os
import sys
import itertools

import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn


class IntOrNoneField(ingredient.Field):
    """
    Simple class that accepts an int or a None
    """

    def is_valid(self, value):
        return isinstance(value, int) or value is None
    
    def coerce(self, value):
        if value is None:
            return value
        return int(value)


class source_extraction2(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Extract sources from a FITS image
    """

    inputs = {
        'images': ingredient.ListField(
            '--images',
            help="List of FITS images"
        ),
        'detection_level': ingredient.FloatField(
            '--detection-level',
            help='Detection level for sources'
        ),
        'dataset_id': IntOrNoneField(
            '--dataset-id',
            help='Dataset to which images belong',
            default=None
        ),
        'radius': ingredient.FloatField(
            '--radius',
            help='relative radius for source association',
            default=1
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
        }

    outputs = {
        'dataset_id': ingredient.IntField()
        }
    
    def go(self):
        self.logger.info("Extracting sources")
        super(source_extraction2, self).go()
        dataset_id = self.inputs['dataset_id']
        
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

        # Get database login details
        dblogin = dict([(key, self.config.get('database', key))
                      for key in ('name', 'user', 'password', 'host')])

        # Running this on nodes, in case we want to perform source extraction
        # on individual images that are still stored on the compute nodes
        # Note that for that option, we will need host <-> data mapping,
        # eg VDS files
        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for image in self.inputs['images']:
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image,
                        self.inputs['detection_level'],
                        dataset_id,
                        self.inputs['radius'],
                        dblogin
                        ]
                    )
                )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        dataset_id = jobs[0].results['dataset_id']
        self.outputs['dataset_id'] = dataset_id
                
        #                Check if we recorded a failing process before returning
        # ----------------------------------------------------------------------
        if self.error.isSet():
            self.logger.warn("Failed source extraction process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(source_extraction2().main())
