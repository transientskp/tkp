# Convenience script to run TKP unit tests.

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
import sys
import logging
import tkp.tests

# Suppress annoying warning messages -- we'll catch errors
# due to test failures rather than log messages.
logging.basicConfig(level=logging.CRITICAL)

args = ['tkp.tests.' + arg for arg in sys.argv[1:]]
if args:
    testfiles = [testfile for testfile in tkp.tests.testfiles if testfile in args]
else:
    testfiles = tkp.tests.testfiles

# If we can't import a particular module, we should warn the user and move on
# with the test suite, rather than bailing out completely. However, we log
# this as a failure.
exit_on_success = 0
for test in testfiles:
    try:
        __import__(test)
    except ImportError, e:
        print >>sys.stderr, "ERROR: Not running %s: required module failed to import (%s)" % (test, e)
        testfiles.remove(test)
        # return non-zero if we have skipped a testfile
        exit_on_success = 1

result = unittest.TextTestRunner(verbosity=2).run(
    unittest.TestLoader().loadTestsFromNames(testfiles)
    )

if result.wasSuccessful():
    sys.exit(exit_on_success)
else:
    sys.exit(1)
