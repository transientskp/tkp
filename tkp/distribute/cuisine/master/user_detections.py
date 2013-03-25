import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.parset import parameterset
from lofarpipe.support.remotecommand import ComputeJob
from tkp.db import monitoringlist as dbmon
from tkp.db import general as dbgen
from tkp.db.orm import Image
from tkp.distribute.cuisine.common import TrapMaster, nodes_available


class user_detections(TrapMaster):
    """Get the user entries in an image (ie user detections), do a forced fit and 
    append the results to extractedsources into the database"""

    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="user_detection configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    def trapstep(self):
        parset_file = self.inputs['parset']
        parset = parameterset(parset_file)
        deRuiter_radius = parset.getFloat('deRuiter_radius', 3.717)

        image_ids = self.inputs['args']
        image_paths = [Image(id=id).url for id in image_ids]

        self.logger.info("starting user_detections for images %s" % image_ids)

        image_uds = [dbmon.get_userdetections(image_id) for image_id in image_ids]
        ff_uds = self.distributed(image_ids, image_paths, image_uds)

        for (image_id, ff_ud) in ff_uds:
            dbgen.insert_extracted_sources(image_id, ff_ud, 'ff_ud')
            dbgen.filter_userdetections_extracted_sources(image_id, deRuiter_radius)


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
                        image_nd
                    ]
                )
            )

        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        results = []
        for job in jobs.itervalues():
            if 'ff_ud' in job.results:
                ff_ud = job.results['ff_ud']
                image_id = job.results['image_id']
                results.append((image_id, ff_ud))
            else:
                self.error.set()
        return results
