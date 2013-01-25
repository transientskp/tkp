from __future__ import with_statement
from __future__ import division
import sys
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.utilities import log_time
from tkp.database.utils import monitoringlist as dbmon
import trap.ingredients as ingred

class transient_search(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Search for transients in the database
    """

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
        super(transient_search, self).go()
        image_id = self.inputs['args'][0]
        parset = self.inputs['parset']
        transients = ingred.transient_search.search_transients(image_id, parset)
        dbmon.adjust_transients_in_monitoringlist(image_id, transients)
        self.outputs['transients'] = transients

        if self.error.isSet():
            self.logger.warn("Failed transient search process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(transient_search().main())
