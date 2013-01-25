import trap.recipes
import trap.ingredients as ingred

class mon_detections(trap.recipes.TrapNode):
    def trapstep(self, image, md, parset_file):
        self.outputs['ff_mon'] = ingred.source_extraction.forced_fits(image, md, parset_file)

trap.recipes.node_run(__name__, mon_detections)

