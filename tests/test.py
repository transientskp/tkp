# Convenience script to run TKP unit tests.

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
import sys
import os
import logging
import tkp.tests
import tkp.config
import argparse


# Suppress annoying warning messages -- we'll catch errors
# due to test failures rather than log messages.
logging.basicConfig(level=logging.CRITICAL)

# Catch datapath option; necessary for in-build testing
parser = argparse.ArgumentParser()
parser.add_argument('tests', nargs='+')
parser.add_argument('--datapath')
args = parser.parse_args()
if args.datapath:
    if os.access(args.datapath, os.R_OK):
        tkp.config.config['test']['datapath'] = args.datapath

args = ['tkp.tests.' + arg for arg in args.tests]
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
        sys.stdout.write("ERROR: Not running %s: required module failed to "
                         "import (%s)\n" % (test, e))
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
