from __future__ import with_statement

"""

This recipe extracts characteristics ("features") from the variable light curve,
such as the duration, flux increase.

To do:

  - separate out the main loop over different compute nodes

  - calculate a variability measurement (use Bayesian blocks?)

  - extract non-light curve features (spectral slopes, source associations)
  
"""


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2010-07-28'


SECONDS_IN_DAY = 86400.

import sys, os
from datetime import timedelta
import pickle
import itertools

from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support import lofaringredient
import tkp.database.database
import monetdb.sql.connections


SQL = """\
UPDATE transients
SET status = %s
WHERE xtrsrc_id = %s
"""


class DBConnectionField(lofaringredient.Field):
    def is_valid(self, value):
        return isinstance(value, monetdb.sql.connections.Connection)


class DataBaseField(lofaringredient.Field):
    def is_valid(self, value):
        return isinstance(value, tkp.database.database.DataBase)


class feature_extraction(BaseRecipe, RemoteCommandRecipeMixIn):

    inputs = dict(
        dblogin=lofaringredient.DictField(
            '--dblogin',
            help=""),
#        dbconnection=DBConnectionField(
#            '--dbconnection',
#            help=""),
        database=DataBaseField(
            '--database',
            help='DataBase object'
        ),
        transients=lofaringredient.ListField(
            '--transients',
            help=""),
        nproc=lofaringredient.IntField(
            '--nproc',
            default=8,
            help="Maximum number of simultaneous processes per output node"),
        )
    outputs = dict(
        transients=lofaringredient.ListField()
        )

    def go(self):
        super(feature_extraction, self).go()
        self.database = self.inputs['database']
        self.logger.info("transients = %s" % str(self.inputs['transients']))

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
        for transient in self.inputs['transients']:
            node = nodes.next()
            jobs.append(
                ComputeJob(
                    node,
                    command,
                    arguments=[
                        transient,
                        self.inputs['dblogin']
                        ]
                    )
                )
        self.logger.info("Scheduling jobs")
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        self.logger.info("Getting Transient objects")
        self.outputs['transients'] = [job.results['transient'] for job in jobs.itervalues()]
                        
        if self.error.isSet():
            return 1
        else:
            return 0


if __name__ == '__main__':
    sys.exit(feature_extraction().main())
