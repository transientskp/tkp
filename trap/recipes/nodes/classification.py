import trap.ingredients.classification
from trap.ingredients.common import TrapNode, node_run
import trap.recipes

class classification(TrapNode):
    def trapstep(self, transient, parset, tkpconfigdir=None):
        self.outputs['transient'] = trap.ingredients.classification.classify(transient,
                                        parset, tkpconfigdir)

node_run(__name__, classification)

