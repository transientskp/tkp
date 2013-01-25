import trap.ingredients.quality
import trap.recipes

class quality_check(trap.recipes.TrapNode):
    def trapstep(self, id, image_path, parset_file):
            self.outputs['rejected'] = trap.ingredients.quality.reject_check(id, image_path, parset_file)

trap.recipes.node_run(__name__, quality_check)
