from __future__ import with_statement

"""

This recipe tries to classify one or more transients according to their
features.

Returned is a dictionary of weights (attached to the Transient object),
where each key is the type of potential source, and the value is the
corresponding weight, ie, some form of likelihood.

A cutoff parameter designates which potential sources are ignored, ie,
source classifications  with weights that fall below this parameter are
removed.

A Transient can obtain multiple source classification which don't
necessary exclude each other. Eg, 'fast transient' and 'gamma-ray burst
prompt emission' go perfectly fine together.
The first ensures some rapid action can be taken, while the latter could
alert the right people to the transient (the GRB classification could
follow from a combination of 'fast transient' and an external trigger).

"""


__author__ = 'Evert Rol / LOFAR Transients Key Project'
__email__ = 'discovery@transientskp.org'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010-2012, University of Amsterdam'
__version__ = '0.2'
__last_modification__ = '2012-01-20'


import sys
import os
import itertools
import datetime
from contextlib import closing

from tkp.database.database import DataBase
import tkp.database.utils as dbutils

from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support import lofaringredient

import tkp.config
import tkp.classification
import tkp.classification.manual
from tkp.classification.manual.classifier import Classifier
from tkp.classification.transient import Position
from tkp.classification.transient import DateTime


class classification(BaseRecipe, RemoteCommandRecipeMixIn):

    inputs = dict(
        weight_cutoff=lofaringredient.FloatField(
            '--weight-cutoff',
            help='Weight cutoff'),
        transients=lofaringredient.ListField(
            '--transients',
            help="List of transient objects"),
        nproc=lofaringredient.IntField(
            '--nproc',
            default=8,
            help="Maximum number of simultaneous processes per output node"),
        )
    outputs = dict(
        transients=lofaringredient.ListField()
        )

    def go(self):
        super(classification, self).go()
        transients = self.inputs['transients']
        weight_cutoff = float(self.inputs['weight_cutoff'])
        # Some dummy data
        position = Position(123.454, 12.342, error=0.0008)
        timezero = DateTime(2010, 2, 3, 16, 35, 31, error=2)

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
        self.logger.info("available nodes = %s" % str(available_nodes))    

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        nodes = itertools.cycle(nodes)
        for transient in transients:
            node = nodes.next()
            self.logger.info("Executing classification for %s on node %s" % (transient, node))
            jobs.append(
                ComputeJob(node, command, arguments=[
                transient, weight_cutoff, tkp.config.CONFIGDIR]))

        self.logger.info("Scheduling jobs")
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        self.logger.info("Getting Transient objects")
        self.outputs['transients'] = [job.results['transient'] for job in jobs.itervalues()]
        # Store or update transients in database
        # Note: we do this here, to avoid compute nodes blocking each other
        # Things can probably be done a bit more efficient though
        with closing(DataBase()) as database:
            self.logger.info("Storing/updating transient into database")
            for transient in self.outputs['transients']:
                if isinstance(transient.timezero, DateTime):
                    t_start = transient.timezero.datetime
                elif isinstance(transient.timezero, datetime.datetime):
                    t_start = transient.timezero
                else:
                    t_start = datetime.datetime(1970, 1, 1)
        if self.error.isSet():
            return 1
        else:
            return 0


if __name__ == '__main__':
    sys.exit(classification().main())
