"""Run all test_*.py files in tests/, stopping at the first failure or error."""

import sys
import unittest
from pathlib import Path


def main():
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    tests_dir = Path(__file__).resolve().parent / "tests"
    suite = unittest.defaultTestLoader.discover(str(tests_dir), pattern="test_*.py")
    if suite.countTestCases() == 0:
        print("FAILURE: No tests found.")
        return 1

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, failfast=True)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("SUCCESS: All tests passed.")
        return 0

    print("FAILURE: Tests stopped after the first failure or error.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
