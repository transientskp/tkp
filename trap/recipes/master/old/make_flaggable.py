#                                                         LOFAR IMAGING PIPELINE
#
#                Make an MS flaggable; wraps makeFLAGwritable (but doesn't fork)
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
import os

import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.group_data import load_data_map
from lofarpipe.support.remotecommand import ComputeJob

class make_flaggable(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Update the storage manager on an MS to make the flag column writable.
    """
    inputs = {
        'makeflagwritable': ingredient.ExecField(
            '--makeFLAGwritable',
            help="Path to makeFLAGwritable script",
            default='/opt/LofIm/daily/lofar/bin/makeFLAGwritable'
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
        self.logger.info("Starting make_flaggable run")
        super(make_flaggable, self).go()

        #                       Load file <-> compute node mapping from disk
        # ------------------------------------------------------------------
        self.logger.debug("Loading map from %s" % self.inputs['args'][0])
        data = load_data_map(self.inputs['args'][0])

        command = "python %s" % (self.__file__.replace('master', 'nodes'))
        jobs = []
        for host, ms in data:
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        ms,
                        self.inputs['makeflagwritable']
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
    sys.exit(make_flaggable().main())
