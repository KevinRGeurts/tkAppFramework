# Standard
import unittest
import tkinter as tk
from tkinter import ttk

# Local
from tkApp import tkApp
from test_tkViewManager import TesttkViewManager


class TesttkApp(tkApp):
    """
    Class is a very simple child of tkApp, intended only to provide an implementation of _createViewManager(...) factory method,
    to facilitate unit testing.
    """
    def _createViewManager(self):
        """
        Concrete Implementation, which returns a TesttkViewManager instance.
        :return: tkViewManager instance that will be the app's view manager
        """
        return TesttkViewManager(self)


class Test_tkApp(unittest.TestCase):
    def test_init_exit(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App')
        self.assertEqual(root.title(), 'Test App')
        self.assertEqual(TesttkViewManager, type(app._view_manager))
        self.assertIsNone(app.onFileExit())


if __name__ == '__main__':
    unittest.main()
