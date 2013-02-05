from __future__ import with_statement
import itertools
import lofarpipe.support.lofaringredient as ingredient
from tkp.database.orm import Image
from lofarpipe.support.remotecommand import ComputeJob
import tkp.database.utils.general as dbgen
import trap.ingredients as ingred
from trap.ingredients.common import TrapMaster


class insert_sources(TrapMaster):
    """Extract sources from a FITS image"""

    inputs = {
        #'parset': ingredient.FileField(
        #    '-p', '--parset',
        #    dest='parset',
        #    help="Source finder configuration parset"
        #),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
    }

    def trapstep(self):
        self.logger.info("Inserting blindly extracted sources...")

        #sources_sets = self.inputs['source_sets']
        image_id = self.inputs['args'][0]
        sources = self.inputs['args'][1]
        #self.logger.info("IS: Inserting %s sources for image ID %s" % (len(sources), image_id))
        #for (image_id, sources) in sources_sets:
        #    dbgen.insert_extracted_sources(image_id, sources, 'blind')
        dbgen.insert_extracted_sources(image_id, sources, 'blind')

