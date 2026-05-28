"""
This module provides unit tests for tkDGElement class and children.
"""


# Standard
import unittest


# Local

from tkAppFramework.tkdatagridwidget import tkDGElement
from tkAppFramework.ObserverPatternBase import Observer



class Test_tkDGElement(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk()

    def tearDown(self):
        if self.root:
            self.root.destroy()

    def test_init(self):
        o = Observer()
        e = tkDGElement(o)
        self.assertEqual(len(e._observers), 1)
        self.assertIsNone(e._element_widget)
        self.assertTupleEqual(e.get_state(),(tkDGElement, None))
        self.assertIsNone(e.canvasID)

    def test_set_state(self):
        o = Observer()
        e = tkDGElement(o)
        x=0
        def f():
            nonlocal x
            x+=1
        o.register_subject(e, f)
        e.set_state(1)
        self.assertEqual(1, x)


if __name__ == '__main__':
    unittest.main()
