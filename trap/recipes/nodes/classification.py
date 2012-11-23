import trap.ingredients.classification
import trap.recipes

class classification(trap.recipes.TrapNode):
    def trapstep(self, transient, parset, tkpconfigdir=None):
        self.outputs['transient'] = trap.ingredients.classification.classify(transient,
                                        parset, tkpconfigdir)

trap.recipes.node_run(__name__, classification)

