"""
This module provides unit tests for the SimulatorAdapter class.
"""


# Standard
import unittest
import logging

# Local
from tkAppFramework.sim_adapter import SimulatorAdapter


class Test_SimulatorAdapter(unittest.TestCase):
    def setUp(self):
        # Create a logger called 'test_simulator_adapter_logger' This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('test_simulator_adapter_logger')
        # This is the threshold level for the logger itself, before it will pass to any handlers, which can have their own threshold.
        # Should be able to control here what the stream handler receives and thus what ends up going to stderr.
        # Use this key for now:
        #   DEBUG = debug messages sent to this logger will end up on stderr
        #   INFO = info messages sent to this logger will end up on stderr
        logger.setLevel(logging.INFO)
        # Set up this highest level below root logger with a stream handler
        sh = logging.StreamHandler()
        # Set the threshold for the stream handler itself, which will come into play only after the logger threshold is met.
        sh.setLevel(logging.INFO)
        # Add the stream handler to the logger
        logger.addHandler(sh)        
    
    def test_init_set_get_simulator(self):
        # Here our dummy test simulator can be literaly anything. Here a float.
        test_sim = float(19.0)
        # Test __init__ and @property getter
        adapt = SimulatorAdapter(sim=test_sim, logger_name='test_simulator_adapter_logger')
        self.assertEqual(id(adapt.simulator), id(test_sim))
        # Test @property setter
        test_sim = float(99.0)
        adapt.simulator = test_sim
        self.assertEqual(id(adapt.simulator), id(test_sim))

    def test_run(self):
        adapt = SimulatorAdapter(logger_name='test_simulator_adapter_logger')
        # Test that expected info is logged
        with self.assertLogs('test_simulator_adapter_logger', level=logging.INFO) as cm:
            adapt.run()
        # Test that the info messages sent to the logger are as expected
        self.assertEqual(cm.output[0], 'INFO:test_simulator_adapter_logger:<<SimulatorReportsCompletion>>')    

    def test_load_and_run(self):
        adapt = SimulatorAdapter(logger_name='test_simulator_adapter_logger')
        # Test that expected info is logged
        with self.assertLogs('test_simulator_adapter_logger', level=logging.INFO) as cm:
            adapt.load_and_run()
        # Test that the info messages sent to the logger are as expected
        self.assertEqual(cm.output[0], 'INFO:test_simulator_adapter_logger:<<SimulatorReportsCompletion>>')    


if __name__ == '__main__':
    unittest.main()
