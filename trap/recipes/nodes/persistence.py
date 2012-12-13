import trap.ingredients.persistence
import trap.recipes

class persistence(trap.recipes.TrapNode):
    def trapstep(self, image,  parset_file):
        self.outputs['metadatas'] = trap.ingredients.persistence.node_steps([image], parset_file)

trap.recipes.node_run(__name__, persistence)

