"""
This module provides unit tests for tkApp class.
"""


# Standard
import unittest
import tkinter as tk
from tkinter import ttk

# Local
from dummy_AppModelViewMgr import TesttkApp, TesttkViewManager
from model import Model


class Test_tkApp(unittest.TestCase):
    def test_init_exit(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        self.assertEqual(root.title(), 'Test App')
        self.assertIsInstance(app._view_manager, TesttkViewManager)
        self.assertIsInstance(app.getModel(), Model)
        self.assertIs(app.getModel(), app._model)
        self.assertIsNone(app.onFileExit())


if __name__ == '__main__':
    unittest.main()
