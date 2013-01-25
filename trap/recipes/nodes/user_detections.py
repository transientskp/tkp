import trap.ingredients as ingred
import trap.recipes

class user_detections(trap.recipes.TrapNode):
    
    def trapstep(self, image, ud, parset_file):
        self.outputs['ff_ud'] = ingred.source_extraction.forced_fits(image, ud, parset_file)

trap.recipes.node_run(__name__, user_detections)

