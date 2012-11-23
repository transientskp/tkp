import trap.ingredients.feature_extraction
import trap.recipes

class feature_extraction(trap.recipes.TrapNode):
    def trapstep(self, transient, tkpconfigdir=None):
        self.outputs['transient'] = trap.ingredients.feature_extraction.extract_features(transient)

trap.recipes.node_run(__name__, feature_extraction)
