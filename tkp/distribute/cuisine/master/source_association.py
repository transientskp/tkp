import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.parset import parameterset
from tkp.database import monitoringlist as dbmon
from tkp.database import associations as dbass
from tkp.distribute.cuisine.common import TrapMaster


class source_association(TrapMaster):
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
    
    def trapstep(self):
        self.logger.info("Associating sources")
        image_ids = self.inputs['args']
        self.logger.info("starting source association for images %s" % image_ids)
        parset = self.inputs['parset']
        sa_parset = parameterset(parset)
        deRuiter_radius = sa_parset.getFloat('deRuiter_radius', 3.717)
        self.logger.info("SA De Ruiter radius = %s" % (deRuiter_radius,))
        for image_id in image_ids:
            dbass.associate_extracted_sources(image_id, deRuiter_r=deRuiter_radius)
            dbmon.add_nulldetections(image_id)

