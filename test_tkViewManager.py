# Standard
import unittest
import tkinter as tk
from tkinter import ttk

# Local
from tkViewManager import tkViewManager
from ObserverPatternBase import Subject

class TestWidget(ttk.LabelFrame, Subject):
    """
    Class represents a tkinter label frame widget, for testing tkViewManager.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent, text='Test Widget')
        Subject.__init__(self)


class TesttkViewManager(tkViewManager):
    """
    Class is a very simple child of tkViewManager, intended only to provide an implementation of _CreateWidgets(...),
    to facilitate unit testing.
    """
    def _CreateWidgets(self):
        """
        Concrete Implementation, does nothing, but does not raise NotImplementedError.
        :return None:
        """
        return None
    
    def handle_test_widget_update(self):
        """
        Handle updates from the test widget:
        :return None:
        """
        raise NotImplementedError
        return None


class Test_tkViewManager(unittest.TestCase):
    def test_register_subject(self):
        root = tk.Tk()
        vm = TesttkViewManager(root)
        cw = TestWidget(vm)
        vm.register_subject(cw,vm.handle_test_widget_update)
        self.assertTrue(vm._subjects.__contains__(cw))

    def test_detach(self):
        root = tk.Tk()
        vm = TesttkViewManager(root)
        cw = TestWidget(vm)
        cw.attach(vm)
        self.assertTrue(len(cw._observers)==1)
        vm.register_subject(cw,vm.handle_test_widget_update)
        vm._detach_from_subjects()
        self.assertTrue(len(cw._observers)==0)

    def test_update(self):
        root = tk.Tk()
        vm = TesttkViewManager(root)
        cw = TestWidget(vm)
        cw.attach(vm)
        vm.register_subject(cw,vm.handle_test_widget_update)
        self.assertRaises(NotImplementedError, vm.update, cw)





if __name__ == '__main__':
    unittest.main()