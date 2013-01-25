import trap.ingredients as ingred
import trap.recipes

class null_detections(trap.recipes.TrapNode):
    def trapstep(self, image, nd, parset_file):
        self.outputs['ff_nd'] = ingred.source_extraction.forced_fits(image, nd, parset_file)

trap.recipes.node_run(__name__, null_detections)

