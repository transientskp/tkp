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


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2010-08-05'


import sys
import os
import itertools

import monetdb.sql.connections

from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support import lofaringredient

import tkp.database.database
import tkp.classification
import tkp.classification.manual
from tkp.classification.manual.classifier import Classifier
from tkp.classification.manual.utils import Position
from tkp.classification.manual.utils import DateTime


SQL = dict(DELETE="""\
DELETE FROM classification
WHERE transient_id = (
   SELECT transientid
   FROM transients
   WHERE xtrsrc_id = %s)
""",
           INSERT="""\
INSERT INTO classification
(transient_id, classification, weight)
VALUES ((SELECT transientid FROM transients WHERE xtrsrc_id=%s), %s, %s)
""",
           INSERT2="""\
INSERT INTO classification
(transient_id, classification, weight)
VALUES (%s)
""")



class DataBaseField(lofaringredient.Field):
    def is_valid(self, value):
        return isinstance(value, tkp.database.database.DataBase)


class classification(BaseRecipe, RemoteCommandRecipeMixIn):

    inputs = dict(
        schema=lofaringredient.StringField(
            '--schema',
            help="Python file containing classification schema"),
        weight_cutoff=lofaringredient.FloatField(
            '--weight-cutoff',
            help='Weight cutoff'),
        transients=lofaringredient.ListField(
            '--transients',
            help="List of transient objects"),
        database=DataBaseField(
            '--database',
            help="DataBase object"),
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
        self.database = self.inputs['database']
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
            self.logger.info("Executing classification for transient %s on node %s" % (transient, node))
            jobs.append(
                ComputeJob(node, command, arguments=[
                self.inputs['schema'], self.config.get("layout", "parset_directory"),
                transient, weight_cutoff]))

        self.logger.info("Scheduling jobs")
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        self.logger.info("Getting Transient objects")
        self.outputs['transients'] = [job.results['transient'] for job in jobs.itervalues()]

        if self.error.isSet():
            return 1
        else:
            return 0


if __name__ == '__main__':
    sys.exit(classification().main())
