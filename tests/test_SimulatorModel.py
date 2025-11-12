"""
This module provides unit tests for the SimulatorModel class.
"""


# Standard
import unittest

# Local
from tkAppFramework.SimulatorModel import SimulatorModel
from tkAppFramework.sim_adapter import SimulatorAdapter


class Test_SimulatorModel(unittest.TestCase):
    def test_init_set_get_adapter(self):
        # Test __init__ and @property getter
        adapt1 = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(adapt1)
        self.assertEqual(id(mod.sim_adapter), id(adapt1))
        # Test @property setter
        adapt2 = SimulatorAdapter(logger_name='test_simulator_model_logger2')
        mod.sim_adapter = adapt2
        self.assertEqual(id(mod.sim_adapter), id(adapt2))

    def test_run(self):
        adapt = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(adapt)
        self.assertRaises(NotImplementedError, mod.run)


if __name__ == '__main__':
    unittest.main()
