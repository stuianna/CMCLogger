import unittest
import logging

logging.disable(logging.CRITICAL)

class CheckTests(unittest.TestCase):

    def test_check_tests_work(self):
        self.assertIs(True,True)

if __name__ == '__main__':
    unittest.main();
