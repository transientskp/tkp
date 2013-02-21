from trap.distribute.cuisine.common import TrapNode, node_run
import trap.ingredients.persistence
import trap.distribute.cuisine

class persistence(TrapNode):
    def trapstep(self, image,  parset_file):
        self.outputs['metadatas'] = trap.ingredients.persistence.node_steps([image], parset_file)

node_run(__name__, persistence)
