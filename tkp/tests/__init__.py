import unittest

testfiles = [
    'tkp.tests.coordinates',
    'tkp.tests.gaussian',
    'tkp.tests.L15_12h_const',
    'tkp.tests.utilities',
    'tkp.tests.wcs',
    'tkp.tests.sigmaclip',
    'tkp.tests.source_measurements',
    'tkp.tests.FDR'
]

# Pyrap is required for AIPS++ image support, but
# not necessary for the rest of the library.
try:
    import pyrap
except:
    pass
else:
    testfiles.append('tkp.tests.aipsppimage')
