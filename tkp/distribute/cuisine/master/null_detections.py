import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.remotecommand import ComputeJob
from tkp.db import monitoringlist as dbmon
from tkp.db import general as dbgen
from tkp.db.orm import Image
from tkp.distribute.cuisine.common import TrapMaster, nodes_available
from tkp import steps


class null_detections(TrapMaster):
    """Get the null detections in an image, do a forced fit and 
    append the results to extractedsources into the database"""

    inputs = {
        'parset': ingredient.DictField(
            '-p', '--parset',
            dest='parset',
            help="null_detection configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    def trapstep(self):
        self.parset = self.inputs['parset']
        image_ids = self.inputs['args']
        self.logger.info("starting null_detections for images %s" % image_ids)
        image_paths = [Image(id=id).url for id in image_ids]
        image_nds = [dbmon.get_nulldetections(image_id, self.parset['deruiter_radius']) for image_id in image_ids]
        ff_nds = self.distributed(image_ids, image_paths, image_nds)

        for image_id, ff_nd in ff_nds:
            dbgen.insert_extracted_sources(image_id, ff_nd, 'ff_nd')


    def distributed(self, image_ids, image_paths, image_nds):
        nodes = nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        host = hosts.next()
        for image_id, image_path, image_nd in zip(image_ids, image_paths, image_nds):
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image_id,
                        image_path,
                        image_nd,
                        self.parset
                    ]
                )
        )

        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        results = []
        for job in jobs.itervalues():
            if 'ff_nd' in job.results:
                ff_nd = job.results['ff_nd']
                image_id = job.results['image_id']
                results.append((image_id, ff_nd))
            else:
                self.error.set()
        return results

