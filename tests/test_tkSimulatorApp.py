"""
This module provides unit tests for tkSimulatorApp class.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkSimulatorApp import tkSimulatorApp
from tkSimulatorViewManager import tkSimulatorViewManager
from SimulatorModel import SimulatorModel
from tkApp import AppAboutInfo


class Test_tkSimulatorApp(unittest.TestCase):
    def test_init_exit(self):
        root = tk.Tk()
        simapp = tkSimulatorApp(root)
        self.assertEqual(root.title(), 'Simulator Application')
        self.assertIsInstance(simapp._view_manager, tkSimulatorViewManager)
        self.assertIsInstance(simapp.getModel(), SimulatorModel)
        info = AppAboutInfo(name='Simulator Application', version='0.1', copyright='2025', author='Kevin R. Geurts',
                           license='MIT License', source='https://github.com/KevinRGeurts/tkAppFramework'
                           help_file='.\\Help\\SimApp_HelpFile.txt')
        self.assertTupleEqual(simapp.getAboutInfo(), info)
        self.assertIsNone(simapp.onFileExit())


if __name__ == '__main__':
    unittest.main()
