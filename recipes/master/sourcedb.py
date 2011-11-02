#                                                         LOFAR IMAGING PIPELINE
#
#                                                                sourcedb recipe
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
import os

import lofarpipe.support.utilities as utilities
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.clusterlogger import clusterlogger
from lofarpipe.support.group_data import load_data_map
from lofarpipe.support.remotecommand import ComputeJob

class sourcedb(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Add a source database to input MeasurementSets.

    This recipe is called by the :class:`bbs.bbs` recipe; it may also be used
    standalone.

    **Arguments**

    A mapfile describing the data to be processed.
    """
    inputs = {
        'executable': ingredient.ExecField(
            '--executable',
            help="Full path to makesourcedb executable",
            default="/opt/LofIm/daily/lofar/bin/makesourcedb"
        ),
        'skymodel': ingredient.FileField(
            '-s', '--skymodel',
            dest="skymodel",
            help="Input sky catalogue"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        )
    }

    outputs = {
        'mapfile': ingredient.FileField()
    }

    def go(self):
        self.logger.info("Starting sourcedb run")
        super(sourcedb, self).go()

        #                           Load file <-> compute node mapping from disk
        # ----------------------------------------------------------------------
        self.logger.debug("Loading map from %s" % self.inputs['args'][0])
        data = load_data_map(self.inputs['args'][0])

        command = "python %s" % (self.__file__.replace('master', 'nodes'))
        jobs = []
        for host, ms in data:
            jobs.append(
                ComputeJob(
                    host, command, arguments=[
                        self.inputs['executable'], ms, self.inputs['skymodel']
                    ]
                )
            )
        self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        if self.error.isSet():
            return 1
        else:
            self.outputs['mapfile'] = self.inputs['args'][0]
            return 0

if __name__ == '__main__':
    sys.exit(sourcedb().main())
