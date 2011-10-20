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

import tkp.config
from tkp.database.database import ENGINE


class source_extraction(BaseRecipe, RemoteCommandRecipeMixIn):
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
        'dataset_id': ingredient.IntField(
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

    def go(self):
        self.logger.info("Extracting sources")
        super(source_extraction, self).go()
        self.logger.info("ENGINE = %s", ENGINE)
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
                        tkp.config.CONFIGDIR
                        ]
                    )
                )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        #                Check if we recorded a failing process before returning
        # ----------------------------------------------------------------------
        if self.error.isSet():
            self.logger.warn("Failed source extraction process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(source_extraction().main())
