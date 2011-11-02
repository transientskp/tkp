#                                                         LOFAR IMAGING PIPELINE
#
#                                         New DPPP recipe: fixed node allocation
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement

from itertools import cycle
from contextlib import nested
from collections import defaultdict

import collections
import sys
import os

import lofarpipe.support.utilities as utilities
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.group_data import load_data_map
from lofarpipe.support.parset import Parset

class dppp(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Runs DPPP (either ``NDPPP`` or -- in the unlikely event it's required --
    ``IDPPP``) on a number of MeasurementSets. This is used for compressing
    and/or flagging data

    **Arguments**

    A mapfile describing the data to be processed.
    """
    inputs = {
        'executable': ingredient.ExecField(
            '--executable',
            help="The full path to the relevant DPPP executable"
        ),
        'initscript': ingredient.FileField(
            '--initscript',
            help="The full path to an (Bourne) shell script which will intialise the environment (ie, ``lofarinit.sh``)"
        ),
        'parset': ingredient.FileField(
            '-p', '--parset',
            help="The full path to a DPPP configuration parset. The ``msin`` and ``msout`` keys will be added by this recipe"
        ),
        'suffix': ingredient.StringField(
            '--suffix',
            default=".dppp",
            help="Added to the input filename to generate the output filename"
        ),
        'working_directory': ingredient.StringField(
            '-w', '--working-directory',
            help="Working directory used on output nodes. Results will be written here"
        ),
        # NB times are read from vds file as string
        'data_start_time': ingredient.StringField(
            '--data-start-time',
            default="None",
            help="Start time to be passed to DPPP; used to pad data"
        ),
        'data_end_time': ingredient.StringField(
            '--data-end-time',
            default="None",
            help="End time to be passed to DPPP; used to pad data"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            default=8,
            help="Maximum number of simultaneous processes per output node"
        ),
        'nthreads': ingredient.IntField(
            '--nthreads',
            default=2,
            help="Number of threads per (N)DPPP process"
        ),
        'mapfile': ingredient.StringField(
            '--mapfile',
            help="Filename into which a mapfile describing the output data will be written"
        ),
        'clobber': ingredient.BoolField(
            '--clobber',
            default=False,
            help="If ``True``, pre-existing output files will be removed before processing starts. If ``False``, the pipeline will abort if files already exist with the appropriate output filenames"
        )
    }

    outputs = {
        'mapfile': ingredient.FileField(
            help="The full path to a mapfile describing the processed data"
        ),
        'fullyflagged': ingredient.ListField(
            help="A list of all baselines which were completely flagged in any of the input MeasurementSets"
        )
    }


    def go(self):
        self.logger.info("Starting DPPP run")
        super(dppp, self).go()

        #                Keep track of "Total flagged" messages in the DPPP logs
        # ----------------------------------------------------------------------
        self.logger.searchpatterns["fullyflagged"] = "Fully flagged baselines"

        #                            Load file <-> output node mapping from disk
        # ----------------------------------------------------------------------
        self.logger.debug("Loading map from %s" % self.inputs['args'])
        data = load_data_map(self.inputs['args'][0])


        #       We can use the same node script as the "old" IPython dppp recipe
        # ----------------------------------------------------------------------
        command = "python %s" % (
            self.__file__.replace('master', 'nodes').replace('dppp', 'dppp')
        )
        outnames = collections.defaultdict(list)
        jobs = []
        for host, ms in data:
            outnames[host].append(
                os.path.join(
                    self.inputs['working_directory'],
                    self.inputs['job_name'],
                    os.path.basename(ms.rstrip('/')) + self.inputs['suffix']
                )
            )
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        ms,
                        outnames[host][-1],
                        self.inputs['parset'],
                        self.inputs['executable'],
                        self.inputs['initscript'],
                        self.inputs['data_start_time'],
                        self.inputs['data_end_time'],
                        self.inputs['nthreads'],
                        self.inputs['clobber']
                    ]
                )
            )
        self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        #                                  Log number of fully flagged baselines
        # ----------------------------------------------------------------------
        matches = self.logger.searchpatterns["fullyflagged"].results
        self.logger.searchpatterns.clear() # finished searching
        stripchars = "".join(set("Fully flagged baselines: "))
        baselinecounter = defaultdict(lambda: 0)
        for match in matches:
            for pair in (
                pair.strip(stripchars) for pair in match.getMessage().split(";")
            ):
                baselinecounter[pair] += 1
        self.outputs['fullyflagged'] = baselinecounter.keys()

        if self.error.isSet():
            self.logger.warn("Failed DPPP process detected")
            return 1
        else:
            parset = Parset()
            for host, filenames in outnames.iteritems():
                parset.addStringVector(host, filenames)
            parset.writeFile(self.inputs['mapfile'])
            self.outputs['mapfile'] = self.inputs['mapfile']
            return 0

if __name__ == '__main__':
    sys.exit(dppp().main())
