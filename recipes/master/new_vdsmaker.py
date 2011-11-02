#                                                         LOFAR IMAGING PIPELINE
#
#                                     New vdsmaker recipe: fixed node allocation
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
import sys
import os
import tempfile
import errno
import subprocess

import lofarpipe.support.utilities as utilities
import lofarpipe.support.lofaringredient as ingredient

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.group_data import load_data_map
from lofarpipe.support.pipelinelogging import log_process_output

class new_vdsmaker(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Generate a GVDS file (and, optionally, individual VDS files per subband;
    see the ``unlink`` input parameter) describing a collection of
    MeasurementSets.

    **Arguments**

    A mapfile describing the data to be processed.
    """
    inputs = {
        'gvds': ingredient.StringField(
            '-g', '--gvds',
            help="File name for output GVDS file"
        ),
        'directory': ingredient.DirectoryField(
            '--directory',
            help="Directory for output GVDS file"
        ),
        'makevds': ingredient.ExecField(
            '--makevds',
            help="Full path to makevds executable"
        ),
        'combinevds': ingredient.ExecField(
            '--combinevds',
            help="Full path to combinevds executable"
        ),
        'unlink': ingredient.BoolField(
            '--unlink',
            help="Unlink VDS files after combining",
            default=True
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        )
    }

    outputs = {
        'gvds': ingredient.FileField()
    }

    def go(self):
        super(new_vdsmaker, self).go()

        #                           Load file <-> compute node mapping from disk
        # ----------------------------------------------------------------------
        self.logger.debug("Loading map from %s" % self.inputs['args'][0])
        data = load_data_map(self.inputs['args'][0])

        command = "python %s" % (
            self.__file__.replace('master', 'nodes').replace('new_vdsmaker', 'vdsmaker')
        )
        jobs = []
        vdsnames = []
        for host, ms in data:
            vdsnames.append(
                "%s/%s.vds" % (self.inputs['directory'], os.path.basename(ms.rstrip('/')))
            )
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        ms,
                        self.config.get('cluster', 'clusterdesc'),
                        vdsnames[-1],
                        self.inputs['makevds']
                    ]
                )
            )
        self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        if self.error.isSet():
            self.logger.warn("Failed vdsmaker process detected")
            return 1

        # Combine VDS files to produce GDS
        failure = False
        self.logger.info("Combining VDS files")
        executable = self.inputs['combinevds']
        gvds_out = self.inputs['gvds']
        try:
            command = [executable, gvds_out] + vdsnames
            combineproc = subprocess.Popen(
                command,
                close_fds=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            sout, serr = combineproc.communicate()
            log_process_output(executable, sout, serr, self.logger)
            if combineproc.returncode != 0:
                raise subprocess.CalledProcessError(combineproc.returncode, command)
            self.outputs['gvds'] = gvds_out
        except subprocess.CalledProcessError, cpe:
            self.logger.exception("combinevds failed with status %d: %s" % (cpe.returncode, serr))
            failure = True
        except OSError, e:
            self.logger.error("Failed to spawn combinevds (%s)" % str(e))
            failure = True
        finally:
            if self.inputs["unlink"]:
                self.logger.debug("Unlinking temporary files")
                for file in vdsnames:
                    os.unlink(file)
            self.logger.info("vdsmaker done")
        if failure:
            self.logger.info("Failure was set")
            return 1
        elif not self.outputs.complete():
            self.logger.info("Outputs incomplete")
        else:
            return 0

if __name__ == '__main__':
    sys.exit(new_vdsmaker().main())
