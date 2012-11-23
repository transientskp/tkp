import trap.ingredients.quality
import trap.recipes

class quality_check(trap.recipes.TrapNode):
    def trapstep(self, image_id, parset_file):
            self.outputs['image_id'] = image_id
            self.outputs['pass'] = trap.ingredients.quality.check(image_id,
                                                            parset_file)

trap.recipes.node_run(__name__, quality_check)
