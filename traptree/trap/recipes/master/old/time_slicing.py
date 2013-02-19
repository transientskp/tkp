from __future__ import with_statement

import os
import sys
import time
import itertools

from pyrap.quanta import quantity

import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.parset import Parset
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.group_data import store_data_map


class IntervalField(ingredient.StringField):
    """Field that contains a time interval

    Allowed formats are:

        - seconds

        - hh:mm:ss

        - hh:mm:ss.sss

    """

    def is_valid(self, value):
        return isinstance(value, float)

    def coerce(self, value):
        try:
            hours, minutes, seconds = value.split(':')
            hours, minutes, seconds = int(hours), int(minutes), float(seconds)
            seconds += 3600*hours + 60*minutes
        except ValueError:  # too many or too few items
            try:
                seconds = float(value)
            except ValueError:
                raise TypeError("%s is not a valid time interval format" % value)
        return seconds
                        

class time_slicing(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Create time slices from the data

    """

    inputs = {
        'interval': IntervalField(
            '--interval',
            help="Time interval to slice data into"
        ),
        'gvds_file': ingredient.FileField(
            '--gvds-file',
            help="Global VDS file to obtain time information"
            ),
        'mapfiledir': ingredient.DirectoryField(
            '--main-vds-dir',
            help="Main directory to store datamapper files"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            default=8,
            help="number of processors to be used per node"
            ),
        }

    outputs = {
        'timesteps': ingredient.ListField(),
        'mapfiles': ingredient.ListField(),
        #'gvds': ingredient.ListField()
        #'ms_sets': ingredient.ListField()
        }
    
    def go(self):
        super(time_slicing, self).go()

        self.outputs['mapfiles'] = []
        self.outputs['timesteps'] = []
        #                            Read data for processing from the GVDS file
        # ----------------------------------------------------------------------
        gvds = Parset(self.inputs['gvds_file'])
        data = []
        for part in range(gvds.getInt('NParts')):
            host = gvds.getString("Part%d.FileSys" % part).split(":")[0]
            vds  = gvds.getString("Part%d.Name" % part)
            data.append((host, vds))

        working_dir = os.path.dirname(gvds['Part0.FileName'].getString())
        start_time = quantity(gvds['StartTime'].get()).get('s').get_value()
        end_time = quantity(gvds['EndTime'].get()).get('s').get_value()
        timestep = float(self.inputs['interval'])
        timesteps = []
        while start_time+timestep < end_time:
            timesteps.append(
                (
                start_time, start_time+timestep,
                os.path.join(working_dir, str(int(start_time)))
                )
            )
            start_time += timestep
        # last bit gets appenended to previous timestep, ending with
        # a longer timestep instead of a shorter one
        try:
            timesteps[-1] = (timesteps[-1][0], end_time, timesteps[-1][-1])
        except IndexError:    # timestep is longer than observing interval!
            timesteps.append((start_time, end_time,
                              os.path.join(working_dir, str(int(start_time)))))
        # Obtain available nodes
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
        mapfiles = []
        for label, timestep in enumerate(timesteps):
            command = "python %s" % (self.__file__.replace('master', 'nodes'))
            jobs = []
            start_time, end_time, resultsdir = timestep
            for host, vds in data:
                path = Parset(vds).getString("FileName")
                msname = os.path.basename(path)
                jobs.append(
                    ComputeJob(
                        host, command,
                        arguments=[
                            path,
                            host,
                            resultsdir,
                            start_time,
                            end_time
                        ]
                    )
                )
            jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

            if self.error.isSet():
                self.logger.warn("Failed time-slicing process detected")
                return 1

            # Create a subdirectory based on the start time of the slice
            subdir = "%d" % int(start_time)
            outdir = os.path.join(self.inputs['mapfiledir'], subdir)
            mapfile = os.path.join(outdir, 'mapfile')
            try:
                os.mkdir(outdir)
            except OSError:  # directory already exists
                pass
            # Create a mapping object and safe the results into a mapfile
            mapper = []
            for job in jobs.itervalues():
                mapper.append(job.results['output'])
                #mapper.setdefault(host, []).append(output)
            store_data_map(mapfile, mapper)
            self.outputs['mapfiles'].append(mapfile)
            self.outputs['timesteps'].append((start_time, end_time))

        #                Check if we recorded a failing process before returning
        # ----------------------------------------------------------------------
        if self.error.isSet():
            self.logger.warn("Failed time slicing process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(source_extraction().main())
