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

class mon_detections(BaseRecipe, RemoteCommandRecipeMixIn):
    """Get the monitoring sources that weren't found by the sourcefinder nor 
    were added as null detections to extractedsource. Do a forced fit
    at the positions and append the results to extractedsources into the database"""
    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="persistence configuration parset"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    def go(self):
        super(mon_detections, self).go()
        parset_file = self.inputs['parset']
        
        image_detections = self.inputs['args'][0]
        image = image_detections['image_qualified']['image']
        good_image = image_detections['image_qualified']['good_image']
        image_id = self.inputs['args'][1]
        
        if good_image:
            parset = parameterset(parset_file)
            deRuiter_radius = parset.getFloat('deRuiter_radius', 3.717)
            md = dbmon.get_nulldetections(image_id, deRuiter_radius)
        
            # TODO: How to be sure that the correct node executes the forced fits
            # on the correct image.
            ff_md = self.distributed(image, md, parset_file)
            #ff_mon = ingred.source_extraction.forced_fits(image, mon_detections)
            
            forced_fits = ff_md[0]['forced_fits']
            dbgen.insert_extracted_sources(image_id, forced_fits, 'ff_mon')

        if self.error.isSet():
            self.logger.warn("Failed mon_detections process detected")
            return 1
        else:
            return 0

    def distributed(self, image, md, parset_file):
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
                    md,
                    parset_file,
                ]
            )
        )

        jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])
        ff_mon = []
        for job in jobs.itervalues():
                if 'ff_mon' in job.results:
                    ff_mon.append(job.results['ff_mon'])
        return ff_mon

if __name__ == '__main__':
    sys.exit(mon_detections().main())
