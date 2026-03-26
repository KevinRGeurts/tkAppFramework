"""
This module provides unit tests for tkAppAboutDialog class.
"""


# Standard
import unittest
import tkinter as tk
import sysconfig

# Local
from tkAppFramework.tk_app_about_dlg import tkAppAboutDialog
from tkAppFramework.tkApp import AppAboutInfo


class Test_tkAppAboutDialog(unittest.TestCase):
    def test_init_destroy(self):
        # root = tk.Tk()
        about_info = AppAboutInfo()
        dlg = tkAppAboutDialog(about_info)
        self.assertIsNone(dlg.onDestroyWindow())


if __name__ == '__main__':
    unittest.main()
