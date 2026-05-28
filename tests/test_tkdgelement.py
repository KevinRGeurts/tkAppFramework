"""
This module provides unit tests for tkDGElement class and children.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.datagriddemoapp import DataGridDemotkApp
from tkAppFramework.tkdatagridwidget import tkDGElementText
from tkAppFramework.ObserverPatternBase import Observer


class Test_tkDGElement(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.dgapp = DataGridDemotkApp(self.root)
        self.dg = self.dgapp._view_manager._dg

    def tearDown(self):
        if self.root:
            self.root.destroy()

    def test_init(self):
        e = self.dg.get_grid_element('Base', 0)
        self.assertEqual(e._observers[0], self.dg)
        self.assertIsNotNone(e.elementWidget)
        self.assertIsNotNone(e._element_value)
        self.assertIsNotNone(e.canvasID)
        self.assertTupleEqual(e.get_state(),(tkDGElementText, '0'))

    def test_set_state(self):
        e = self.dg.get_grid_element('Base', 0)
        e.set_state('1')
        self.assertEqual('1', e.get_state()[1])


if __name__ == '__main__':
    unittest.main()
