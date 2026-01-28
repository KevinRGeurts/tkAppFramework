"""
This module provides unit tests for the SimulatorModel class.
"""


# Standard
import unittest
import tkinter as tk
import logging

# Local
from tkAppFramework.SimulatorModel import SimulatorModel
from tkAppFramework.sim_adapter import SimulatorAdapter
from tkAppFramework.dummy_AppViewMgr import TesttkApp


class Test_SimulatorModel(unittest.TestCase):
    def setUp(self):
        # Create a logger called 'test_simulator_model_logger' This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('test_simulator_model_logger')
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

    def test_init_set_get_adapter(self):
        root = tk.Tk()
        app = TesttkApp(root)
        # Test __init__ and @property getter
        adapt1 = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(app, adapt1)
        self.assertEqual(id(mod.sim_adapter), id(adapt1))
        # Test @property setter
        adapt2 = SimulatorAdapter(logger_name='test_simulator_model_logger2')
        mod.sim_adapter = adapt2
        self.assertEqual(id(mod.sim_adapter), id(adapt2))

    def test_run(self):
        root = tk.Tk()
        app = TesttkApp(root)
        adapt = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(app, adapt)
        # Test that expected info is logged
        with self.assertLogs('test_simulator_model_logger', level=logging.INFO) as cm:
            mod.run()
        # Test that the info messages sent to the logger are as expected
        self.assertEqual(cm.output[0], 'INFO:test_simulator_model_logger:<<SimulatorReportsCompletion>>')    

    def test_load_and_run(self):
        root = tk.Tk()
        app = TesttkApp(root)
        adapt = SimulatorAdapter(logger_name='test_simulator_model_logger')
        mod = SimulatorModel(app, adapt)
        # Test that expected info is logged
        with self.assertLogs('test_simulator_model_logger', level=logging.INFO) as cm:
            mod.load_and_run()
        # Test that the info messages sent to the logger are as expected
        self.assertEqual(cm.output[0], 'INFO:test_simulator_model_logger:<<SimulatorReportsCompletion>>')


if __name__ == '__main__':
    unittest.main()
