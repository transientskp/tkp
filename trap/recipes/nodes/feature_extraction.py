from trap.ingredients.common import TrapNode, node_run
import trap.ingredients.feature_extraction
import trap.recipes

class feature_extraction(TrapNode):
    def trapstep(self, transient, tkpconfigdir=None):
        self.outputs['transient'] = trap.ingredients.feature_extraction.extract_features(transient)

node_run(__name__, feature_extraction)
