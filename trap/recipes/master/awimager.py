#                                                         LOFAR IMAGING PIPELINE
#
#                                                                AWimager recipe
#                                     (Based on RFI console and cimager recipes)
#                                                                Evert Rol, 2012
#                                                     discovery@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement

from contextlib import nested
from collections import defaultdict

import sys

import lofarpipe.support.utilities as utilities
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.group_data import load_data_map
from lofarpipe.support.parset import Parset


class awimager(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    The rficonsole recipe runs the rficonsole executable (flagger) across one
    or more MeasurementSets.

    **Arguments**

    A mapfile describing the data to be processed.
    """
    inputs = {
        'executable': ingredient.ExecField(
            '--executable',
            default="/opt/LofIm/lofar/bin/awimager",
            help="Full path to rficonsole executable"
        ),
        'parset': ingredient.FileField(
            '--parset',
            help="AWimager parset",
        ),
        'working_dir': ingredient.StringField(
            '--working-dir',
            default='/tmp',
            help="Temporary rficonsole products are stored under this root on each of the remote machines. This directory should therefore be writable on each machine, but need not be shared across hosts"
        ),

        'nproc': ingredient.IntField(
            '--nproc',
            default=1,
            help="Maximum number of simultaneous processes per node"
        ),        
        'nthreads': ingredient.IntField(
            '--nthreads',
            default=1,
            help="Number of simultaneous threads per process"
        ),        
    }

    outputs = {
        'images': ingredient.ListField(),
        }
    
    def _read_parset(self):
        """Read the parset and convert to a dictionary."""

        # Note: we don't bother with checking whether keywords are valid,
        # or whether they have an appropriate value: every value is
        # read as a string
        parset = Parset(self.inputs['parset'])
        self.options = {}
        for key in parset.keywords():
            self.options[key] = parset.getString(key)
        self.options['nthreads'] = self.inputs['nthreads']
        # Remove "erroneous" keys
        self.options.pop('hdf5', None)
        self.options.pop('fits', None)
        self.options.pop('ms', None)
        self.options.pop('image', None)
        self.options.pop('restored', None)
        
    def go(self):
        self.logger.info("Starting awimager run")
        super(awimager, self).go()
        self.outputs['images'] = []
        
        #                           Load file <-> compute node mapping from disk
        # ----------------------------------------------------------------------
        self.logger.debug("Loading map from %s" % self.inputs['args'])
        datamap = load_data_map(self.inputs['args'][0])
        self._read_parset()
        
        #        Jobs being dispatched to each host are arranged in a dict. Each
        #           entry in the dict is a list of list of filenames to process.
        # ----------------------------------------------------------------------
        hostlist = defaultdict(lambda: list([[]]))
        for host, filename in datamap:
            if (
                self.inputs.has_key('nmeasurementsets') and
                len(hostlist[host][-1]) >= self.inputs['nmeasurementsets']
            ):
                hostlist[host].append([filename])
            else:
                hostlist[host][-1].append(filename)

        command = "python %s" % (self.__file__.replace('master', 'nodes'))
        jobs = []
        operation = self.options.get('operation', 'image')
        for host, file_lists in hostlist.iteritems():
            for file_list in file_lists:
                for msfile in file_list:
                    jobs.append(
                        ComputeJob(
                            host, command,
                            arguments=[
                                self.inputs['executable'],
                                self.options,
                                msfile,
                                self.inputs['working_dir']
                            ]
                        )
                    )
                    # Keep host, image name and MS names together.
                    # We need the latter for proper transfer of the metadata
                    image_name = msfile + ".img"
                    if operation == 'csclean':
                        image_name += ".restored.corr"
                    self.outputs['images'].append((host, image_name, msfile))
        self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        
        if self.error.isSet():
            self.logger.warn("Failed awimager process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(awimager().main())
