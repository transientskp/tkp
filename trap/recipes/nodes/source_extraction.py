import trap.ingredients as ingred
import trap.recipes

class source_extraction(trap.recipes.TrapNode):
    def trapstep(self, image_id, url,  parset, tkpconfigdir=None):
        self.outputs['sources'] = ingred.source_extraction.extract_sources(url, parset, tkpconfigdir)

        # we need to keep track of the image ID also, since we have no good
        # other way to identify the image otherwise
        self.outputs['image_id'] = image_id

trap.recipes.node_run(__name__, source_extraction)

