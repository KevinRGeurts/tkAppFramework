"""
This module provides unit tests for Model class.
"""


# Standard
import unittest

# Local
from model import Model


class Test_Model(unittest.TestCase):
    def test_init(self):
        mod = Model()
        exp_val = 0
        act_val = len(mod._observers)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
