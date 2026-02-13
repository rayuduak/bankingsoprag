import unittest
import sys

loader = unittest.TestLoader()
suite = loader.discover('tests')
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
