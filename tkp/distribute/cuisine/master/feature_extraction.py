from lofarpipe.support import lofaringredient

import tkp.steps.feature_extraction
from tkp.distribute.cuisine.common import TrapMaster


class feature_extraction(TrapMaster):
    outputs = dict(
        transients=lofaringredient.ListField()
        )

    def trapstep(self):
        transients = self.inputs['args']
        "Starting feature extraction"
        new_transients = []
        for transient in transients:
            new_transients.append(tkp.steps.feature_extraction.extract_features(transient))
        self.outputs['transients'] = new_transients

