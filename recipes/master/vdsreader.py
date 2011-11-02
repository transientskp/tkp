#                                                         LOFAR IMAGING PIPELINE
#
#                  vdsreader recipe: extract filenames + metadata from GVDS file
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

import lofarpipe.support.utilities as utilities
import lofarpipe.support.lofaringredient as ingredient

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.utilities import get_parset


class vdsreader(BaseRecipe):
    """
    Read a GVDS file and return a list of the MS filenames referenced therein
    together with selected metadata.

    **Arguments**

    None.
    """
    inputs = {
        'gvds': ingredient.FileField(
            '-g', '--gvds',
            help="GVDS file to process"
        )
    }

    outputs = {
        'data': ingredient.ListField(help="List of MeasurementSet paths"),
        'start_time': ingredient.StringField(help="Start time of observation"),
        'end_time': ingredient.StringField(help="End time of observation"),
        'pointing': ingredient.DictField(help="Observation pointing direction")
    }

    def go(self):
        self.logger.info("Starting vdsreader run")
        super(vdsreader, self).go()

        try:
            gvds = get_parset(self.inputs['gvds'])
        except:
            self.logger.error("Unable to read G(V)DS file")
            raise

        self.logger.info("Building list of measurementsets")
        ms_names = [
            gvds.getString("Part%d.FileName" % (part_no,))
            for part_no in xrange(gvds.getInt("NParts"))
        ]
        self.logger.debug(ms_names)

        self.outputs['data'] = ms_names
        try:
            self.outputs['start_time'] = gvds.getString('StartTime')
            self.outputs['end_time'] = gvds.getString('EndTime')
        except:
            self.logger.warn("Failed to read start/end time from GVDS file")
        try:
            self.outputs['pointing'] = {
                'type': gvds.getStringVector('Extra.FieldDirectionType')[0],
                'dec': gvds.getStringVector('Extra.FieldDirectionDec')[0],
                'ra': gvds.getStringVector('Extra.FieldDirectionRa')[0]
            }
        except:
            self.logger.warn("Failed to read pointing information from GVDS file")
        return 0
