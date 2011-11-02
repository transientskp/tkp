#                                                         LOFAR IMAGING PIPELINE
#
#                                                        Demixing: master script
#                                                             Marcel Loose, 2011
#                                                                loose@astron.nl
# ------------------------------------------------------------------------------

from __future__ import with_statement
import collections
import os
import sys
from optparse import OptionGroup

import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.group_data import load_data_map
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.parset import Parset

class demixing(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Run the demixer on the MS's on the compute nodes.
    """
    inputs = {
        'mapfile': ingredient.StringField(
            '--mapfile',
            help="Name of the output mapfile containing the names of the "
                 "MS-files produced by the demixing recipe"
        ),
        'working_directory': ingredient.StringField(
            '-w', '--working-directory',
            help="Working directory used on output nodes. "
                 "Results will be written here"
        ),
        'initscript': ingredient.FileField(
            '--initscript',
            help="The full path to an (Bourne) shell script which will "
                 "intialise the environment (ie, ``lofarinit.sh``)"
        ),
        'demix_parset_dir': ingredient.DirectoryField(
            '--demix-parset-dir',
            dest='demixdir',
            help="Directory containing the demixing parset-files",
        ),
        'skymodel': ingredient.FileField(
            '--skymodel',
            help="File containing the sky model to use",
        ),
        'demix_sources': ingredient.ListField(
            '--demix-sources',
            dest='remove',
            help="List of sources to remove e.g. 'CygA, CasA'; "
                 "will be determined automatically if not specified.",
            default=[]
        ),
        'ms_target': ingredient.StringField(
            '--ms-target',
            dest='target',
            help="Substring in the output MS name that replaces the "
                 "substring 'uv' (default: 'target')",
            default="target"
        ),
        'timestep': ingredient.IntField(
            '--timestep',
            help="Time step for averaging",
            default=10
        ),
        'freqstep': ingredient.IntField(
            '--freqstep',
            help="Frequency step for averaging",
            default=60
        ),
        'half_window': ingredient.IntField(
            '--half-window',
            help="Window size of median filter",
            default=20
        ),
        'threshold': ingredient.FloatField(
            '--threshold',
            help="Solutions above/below threshold*rms are smoothed",
            default=2.5
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=1
        )
    }

    outputs = {
        'mapfile': ingredient.FileField()
    }


    def go(self):
        self.logger.info("Starting demixing run")
        super(demixing, self).go()

        #                       Load file <-> compute node mapping from disk
        # ------------------------------------------------------------------
        self.logger.debug("Loading map from %s" % self.inputs['args'][0])
        data = load_data_map(self.inputs['args'][0])

        command = "python %s" % (self.__file__.replace('master', 'nodes'))
        outnames = collections.defaultdict(list)
        jobs = []
        job_dir = os.path.join(self.inputs['working_directory'],
                               self.inputs['job_name'])
        for host, ms in data:
            # This is a bit of a kludge. The input MS-filenames are supposed to
            # contain the string "_uv". The demixing node script will produce
            # output MS-files, whose names have the string "_uv" replaced by
            # "_" + self.inputs['ms_target'] + "_sub".
            outnames[host].append(
                os.path.join(
                    job_dir,
                    os.path.basename(ms).replace(
                        '_uv',
                        '_' + self.inputs['ms_target'] + '_sub'
                    )
                )
            )
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        ms,
                        job_dir,
                        self.inputs['initscript'],
                        self.inputs['demix_sources'],
                        self.inputs['ms_target'],
                        self.config.get('cluster', 'clusterdesc'),
                        self.inputs['timestep'],
                        self.inputs['freqstep'],
                        self.inputs['half_window'],
                        self.inputs['threshold'],
                        self.inputs['demix_parset_dir'],
                        self.inputs['skymodel']
                   ]
                )
            )
        self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        if self.error.isSet():
            return 1
        else:
            parset = Parset()
            for host, filenames in outnames.iteritems():
                parset.addStringVector(host, filenames)
            self.logger.debug("Writing mapfile %s" % self.inputs['mapfile'])
            parset.writeFile(self.inputs['mapfile'])
            self.outputs['mapfile'] = self.inputs['mapfile']
            return 0

if __name__ == '__main__':
    sys.exit(demixing().main())
