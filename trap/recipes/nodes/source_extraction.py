import trap.ingredients as ingred
import trap.recipes

class source_extraction(trap.recipes.TrapNode):
    def trapstep(self, image_qualified,  parset, tkpconfigdir=None):
        self.outputs['images_detections'] = ingred.source_extraction.extract_sources(image_qualified, parset, tkpconfigdir)

trap.recipes.node_run(__name__, source_extraction)

