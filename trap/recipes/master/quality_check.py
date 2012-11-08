"""
This recipe will perform some basic quality checks on a given image.

For now it:
    * Checks if the RMS value of an image is within a acceptable range,
    * More to come.

If an image passes theses tests, the image id will be put in the image_ids
output variable, otherwise an rejection entry with put in the rejection
database table.

stuff you can set in the parset file:

    sigma = 3               # sigma value used for iterave clipping image before RMS calculation
    f = 4                   # determines size of subsection, result will be 1/fth of the image size
    low_bound = 1           # multiplied with noise to define lower threshold
    high_bound = 50         # multiplied with noise to define upper threshold
    frequency = 450000000
    subbandwidth = 200000 # in Hz
    intgr_time = 18654      # integration time in seconds
    configuration = LBA_INNER
    subbands = 10           # number of subbands
    channels = 64           # number of channels
    ncore = 24              # number of core stations
    nremote = 16            # number of remote stations
    nintl = 8                 # number of international stations

"""

import itertools
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob

class quality_check(BaseRecipe, RemoteCommandRecipeMixIn):
    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Quality check configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }
    outputs = {
        'good_image_ids': ingredient.ListField()
    }


    def go(self):
        self.logger.info("Performing quality checks")
        super(quality_check, self).go()
        images = self.inputs['args']
        print 'IMAGES =', images

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

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        for image in images:
            host = hosts.next()
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image,
                        self.inputs['parset'],
                    ]
                )
            )
        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        # TODO: some jobs don't have a 'pass' in it. For now it is unclear why.
        self.outputs['good_image_ids'] = [
                job.results['image_id'] for job in jobs.itervalues() if job.results.get('pass', False)
        ]


        if self.error.isSet():
            self.logger.warn("Failed quality control process detected")
            return 1
        else:
            return 0
