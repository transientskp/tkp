#                                              LOFAR TRANSIENTS IMAGING PIPELINE
#
#                                                   Imager-columns adding recipe
#                                                                Evert Rol, 2012
#                                                      software@transientskp.org
# ------------------------------------------------------------------------------

# See also http://lus.lofar.org/forum/index.php?topic=873.0

from __future__ import with_statement
import os
import sys
from contextlib import contextmanager

import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.group_data import load_data_map, store_data_map



class addimagingcolumns(BaseRecipe, RemoteCommandRecipeMixIn):
    """Simple recipe to add necessary columns to an MS for CASA-based
    images"""

    inputs = {
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
        }
    outputs = {}

    def go(self):
        self.logger.info("Converting CASA images to FITS")
        super(addimagingcolumns, self).go()

        #                            Load file <-> output node mapping from disk
        # ----------------------------------------------------------------------
        mapfile = ''.join(self.inputs['args'])
        self.logger.debug("Loading input-data mapfile: %s" % mapfile)
        mappeddata = load_data_map(mapfile)

        #                          Add imaging columns to each MS in the mapfile
        # ----------------------------------------------------------------------
        command = "python %s" % (self.__file__.replace('master', 'nodes'))
        jobs = []
        for host, ms in mappeddata:
            jobs.append(
                ComputeJob(
                    host,
                    command,
                    arguments=[ms]
                )
            )
        self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        
        #                Check if we recorded a failing process before returning
        # ----------------------------------------------------------------------
        if self.error.isSet():
            self.logger.warn("Failed imager process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(addimagingcolumns().main())
