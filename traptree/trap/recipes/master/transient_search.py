from lofarpipe.support import lofaringredient
from tkp.database.utils import monitoringlist as dbmon
import trap.ingredients as ingred
from trap.ingredients.common import TrapMaster


class transient_search(TrapMaster):
    """Search for transients in the database"""

    inputs = {
        'parset': lofaringredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Transient search configuration parset"
        ),
    }
    outputs = {
        'transients': lofaringredient.ListField(),
    }

    def go(self):
        image_id = self.inputs['args'][0]
        parset = self.inputs['parset']
        transients = ingred.transient_search.search_transients(image_id, parset)
        dbmon.adjust_transients_in_monitoringlist(image_id, transients)
        self.outputs['transients'] = transients

