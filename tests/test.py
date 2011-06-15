# Convenience script to run all TKP unit tests.

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
import sys
print [p for p in sys.path if 'trunk' in p]
import logging
import tkp.tests

# Suppress annoying warning messages -- we'll catch errors
# due to test failures rather than log messages.
logging.basicConfig(level=logging.CRITICAL)

# Check that each of our tests can be imported
# Otherwise, unittest throws confusing errors
for test in tkp.tests.testfiles:
    __import__(test)

args = ['tkp.tests.' + arg for arg in sys.argv[1:]]
if args:
    testfiles = [testfile for testfile in tkp.tests.testfiles if testfile in args]
else:
    testfiles = tkp.tests.testfiles

unittest.TextTestRunner(verbosity=2).run(
    unittest.TestLoader().loadTestsFromNames(testfiles)
)
