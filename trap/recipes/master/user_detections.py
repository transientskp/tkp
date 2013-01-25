from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.parset import parameterset
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from tkp.database.utils import monitoringlist as dbmon
from tkp.database.utils import general as dbgen
import trap.ingredients as ingred


class user_detections(BaseRecipe, RemoteCommandRecipeMixIn):
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

    def go(self):
        super(user_detections, self).go()
        ud_parset_file = self.inputs['parset']
        image_detections = self.inputs['args'][0]
        image_id = self.inputs['args'][1]
        
        image = image_detections['image_qualified']['image']
        good_image = image_detections['image_qualified']['good_image']
        
        if good_image:
            # We need to specify de ruiter radius
            parset = parameterset(ud_parset_file)
            deRuiter_radius = parset.getFloat('deRuiter_radius', 3.717)
            ud = dbmon.get_userdetections(image_id, deRuiter_radius)
        
            ff_ud = self.distributed(image, ud, ud_parset_file)
            forced_fits = ff_ud[0]['forced_fits']
            dbgen.insert_extracted_sources(image_id, forced_fits, 'ff_ud')
            dbgen.filter_userdetections_extracted_sources(image_id, deRuiter_radius)

        if self.error.isSet():
            self.logger.warn("Failed user_detections process detected")
            return 1
        else:
            return 0

    def distributed(self, image, ud, ud_parset_file):
        nodes = ingred.common.nodes_available(self.config)

        command = "python %s" % self.__file__.replace('master', 'nodes')
        jobs = []
        hosts = itertools.cycle(nodes)
        host = hosts.next()
        jobs.append(
            ComputeJob(
                host, command,
                arguments=[
                    image,
                    ud,
                    ud_parset_file,
                ]
            )
        )

        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        ff_ud = []
        for job in jobs.itervalues():
                if 'ff_ud' in job.results:
                    ff_ud.append(job.results['ff_ud'])
        return ff_ud

if __name__ == '__main__':
    sys.exit(user_detections().main())
