from lofarpipe.support import lofaringredient
from tkp.db.monitoringlist import adjust_transients_in_monitoringlist
from tkp import steps
from tkp.distribute.cuisine.common import TrapMaster


class transient_search(TrapMaster):
    """Search for transients in the database"""

    inputs = {
        'parset': lofaringredient.DictField(
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
        transients = steps.transient_search.search_transients(image_id, parset)
        adjust_transients_in_monitoringlist(image_id, transients)
        self.outputs['transients'] = transients

