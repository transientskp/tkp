from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.parset import parameterset
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import tkp.config
from tkp.database.utils import associations as dbass
from tkp.database.utils import monitoringlist as dbmon
import trap.ingredients as ingred


class source_association(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Associate extracted sources in current image with known catalogued sources 
    """

    inputs = {
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Source association configuration parset"
        ),
    }
    
    def go(self):
        self.logger.info("Associating sources")
        super(source_association, self).go()
        image_id = self.inputs['args'][0]
        parset = self.inputs['parset']
        sa_parset = parameterset(parset)
        deRuiter_radius = sa_parset.getFloat('deRuiter_radius', 3.717)
        self.logger.debug("SA De Ruiter radius = %s" % (deRuiter_radius,))
        self.logger.info("SA De Ruiter radius = %s" % (deRuiter_radius,))
        dbass.associate_extracted_sources(image_id, deRuiter_r = deRuiter_radius)
        dbmon.add_nulldetections(image_id)
        # similarly, add user_enries here
        
        if self.error.isSet():
            self.logger.warn("Failed source association process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(source_association().main())
