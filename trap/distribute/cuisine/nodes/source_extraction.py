from trap import steps
from trap.distribute.cuisine.common import TrapNode, node_run


class source_extraction(TrapNode):
    def trapstep(self, image_id, url,  parset):
        self.outputs['sources'] = steps.source_extraction.extract_sources(url, parset)

        # we need to keep track of the image ID also, since we have no good
        # other way to identify the image otherwise
        self.outputs['image_id'] = image_id

node_run(__name__, source_extraction)

