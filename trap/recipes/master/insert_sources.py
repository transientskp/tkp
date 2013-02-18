import tkp.database.utils.general as dbgen
from trap.ingredients.common import TrapMaster

class insert_sources(TrapMaster):
    """Extract sources from a FITS image"""

    def trapstep(self):
        self.logger.info("Inserting blindly extracted sources...")

        image_id = self.inputs['args'][0]
        sources = self.inputs['args'][1]
        dbgen.insert_extracted_sources(image_id, sources, 'blind')

