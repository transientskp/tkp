# Convenience script to run all TKP unit tests.

import unittest
import logging
import tkp.tests

# Suppress annoying warning messages -- we'll catch errors
# due to test failures rather than log messages.
logging.basicConfig(level=logging.CRITICAL)

# Check that each of our tests can be imported
# Otherwise, unittest throws confusing errors
for test in tkp.tests.testfiles:
    __import__(test)

unittest.TextTestRunner(verbosity=2).run(
    unittest.TestLoader().loadTestsFromNames(tkp.tests.testfiles)
)
