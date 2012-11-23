import trap.ingredients.source_extraction
import trap.recipes

class source_extraction(trap.recipes.TrapNode):
    def trapstep(self, image,  parset, tkpconfigdir=None):
        self.outputs['image_id'] = trap.ingredients.source_extraction.extract_sources(image, parset, tkpconfigdir)

trap.recipes.node_run(__name__, source_extraction)

