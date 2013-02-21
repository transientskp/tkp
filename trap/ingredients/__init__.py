"""
The ingredients module is a collection of functions that combine functions
in TKP in a useful way. They are the layer between the TKP functions and
the control functions and frameworks, like the distribution logic.

No implementation specific code (like the LOFAR pipeline logic) should be placed
in this module.
"""
import classification
import feature_extraction
import monitoringlist
import persistence
import prettyprint
import quality
import source_extraction
import transient_search
