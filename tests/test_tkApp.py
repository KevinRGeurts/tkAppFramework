"""
This module provides unit tests for tkApp class.
"""


# Standard
import unittest
import tkinter as tk
from tkinter import ttk
import tempfile

# Local
from tkAppFramework.dummy_AppViewMgr import TesttkApp, TesttkViewManager
from tkAppFramework.model import Model
from tkAppFramework.tkApp import AppAboutInfo, tkHelpApp
from tkAppFramework.tkHelpViewManager import tkHelpViewManager
from tkAppFramework.HelpModel import HelpModel


class Test_tkHelpApp(unittest.TestCase):
    def test_init(self):
        help_content = 'Help file text content'
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as temp_file:
            temp_file.write(help_content)
            temp_file.close()
            root = tk.Tk()
            myapp = tkHelpApp(root, help_file=temp_file.name, help_format='txt')
            self.assertEqual(root.title(), 'Help Application')
            self.assertIsInstance(myapp._view_manager, tkHelpViewManager)
            self.assertIsInstance(myapp.getModel(), HelpModel)
            self.assertIsNone(myapp.onFileExit())

    def test_getAppInfo(self):
        help_content = 'Help file text content'
        with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False) as temp_file:
            temp_file.write(help_content)
            temp_file.close()
            root = tk.Tk()
            myapp = tkHelpApp(root, help_file=temp_file.name, help_format='txt')
            info = AppAboutInfo(name='Help Application', version='0.9.0', copyright='2025', author='Kevin R. Geurts',
                                license='MIT License', source='https://github.com/KevinRGeurts/tkAppFramework',
                                help_file=temp_file.name)
            self.assertTupleEqual(myapp.getAboutInfo(), info)


class Test_tkApp(unittest.TestCase):
    def test_init_exit(self):
        root = tk.Tk()
        app = TesttkApp(root, title='Test App', theme_name='classic')
        self.assertEqual(root.title(), 'Test App')
        self.assertIsInstance(app._view_manager, TesttkViewManager)
        self.assertIsInstance(app.getModel(), Model)
        self.assertIs(app.getModel(), app._model)
        self.assertEqual(ttk.Style().theme_use(),'classic')
        self.assertIsNone(app.onFileExit())

    def test_getAppInfo(self):
        root = tk.Tk()
        info = AppAboutInfo(name='Test App', version='1.0', copyright='2025', author='Tester', license='MIT', source='local repo')
        app = TesttkApp(root, title='Test App', app_info=info)
        self.assertTupleEqual(app.getAboutInfo(), info)


if __name__ == '__main__':
    unittest.main()
