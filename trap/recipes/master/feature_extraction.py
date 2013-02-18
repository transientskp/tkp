import sys
import trap.ingredients.feature_extraction
from lofarpipe.support import lofaringredient
from trap.ingredients.common import TrapMaster


class feature_extraction(TrapMaster):
    outputs = dict(
        transients=lofaringredient.ListField()
        )

    def trapstep(self):
        transients = self.inputs['args']
        "Starting feature extraction"
        new_transients = []
        for transient in transients:
            new_transients.append(trap.ingredients.feature_extraction.extract_features(transient))
        self.outputs['transients'] = new_transients

