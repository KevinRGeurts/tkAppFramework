"""
This module provides unit tests for tkDGElement class and children.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.tkdatagridwidget import tkDGElementText, tkDataGridWidget, FieldType, tkDGElementBool, tkDGElementList, tkDGElementFieldHeader


class Test_tkDGElementText(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._dgw = tkDataGridWidget(self._root, fields_config=[('A Text Field', FieldType.TEXT, 'editable', None)], num_records=1)
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_prop_get_state(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.Entry)
        self.assertIsInstance(e._element_value, tk.StringVar)
        self.assertEqual(e.canvasID, 7)
        self.assertTupleEqual(e.get_state(),(tkDGElementText, ''))

    def test_set_get_default_value(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_default_value('Default Text')
        self.assertEqual(e.get_default_value(), 'Default Text')
        
    def test_set_get_state(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_state('1')
        self.assertTupleEqual(e.get_state(), (tkDGElementText, '1'))

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], 'readonly')
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        exp_val = ('<Key-KP_Enter>', '<Key-Return>', '<<ContextMenu>>', '<Key-Delete>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_state('Some Text')
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementText, ''))


class Test_tkDGElementFieldHeader(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._dgw = tkDataGridWidget(self._root, fields_config=[('A Text Field', FieldType.TEXT, 'editable', None)], num_records=1)
        self._dgw.grid()
        self._header_element = self._dgw._header_elements[0]  # Get the header element for the first field.

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_prop_get_state(self):
        e = self._header_element
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.Entry)
        self.assertIsInstance(e._element_value, tk.StringVar)
        self.assertEqual(e.canvasID, 6)
        self.assertTupleEqual(e.get_state(),(tkDGElementFieldHeader, 'A Text Field'))

    def test_set_state(self):
        e = self._header_element
        e.set_state('Text Field Name')
        self.assertTupleEqual(e.get_state(), (tkDGElementFieldHeader, 'Text Field Name'))

    def test_disable_element_elementWidget_prop(self):
        e = self._header_element
        self.assertEqual(e.elementWidget['state'], 'readonly')
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], 'readonly')

    def test_bindings(self):
        e = self._header_element
        exp_val = ('<<ContextMenu>>', '<Key-Delete>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_state('Some Text')
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementText, ''))


class Test_tkDGElementBool(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._dgw = tkDataGridWidget(self._root, fields_config=[('A Boolean Field', FieldType.BOOL, 'editable')], num_records=1)
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_prop_get_state(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.Checkbutton)
        self.assertIsInstance(e._element_value, tk.IntVar)
        self.assertEqual(e.canvasID, 7)
        self.assertTupleEqual(e.get_state(),(tkDGElementBool, 0))

    def test_set_state(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        e.set_state(True)
        self.assertTupleEqual(e.get_state(), (tkDGElementBool, 1))

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], tk.DISABLED)
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        exp_val = ('<<ContextMenu>>', '<Key-Delete>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        e.set_state(True)
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementBool, 0))


class Test_tkDGElementList(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._dgw = tkDataGridWidget(self._root, fields_config=[('A List Field', FieldType.LIST, 'editable')], num_records=1)
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_prop_get_state(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.OptionMenu)
        self.assertIsInstance(e._element_value, tk.StringVar)
        self.assertEqual(e.canvasID, 7)
        self.assertTupleEqual(e.get_state(),(tkDGElementList, ''))

    def test_set_state(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        e.set_menu_choices(('Option 1', 'Option 2', 'Option 3'))
        e.set_state('Option 2')
        self.assertTupleEqual(e.get_state(), (tkDGElementList, 'Option 2'))

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], tk.DISABLED)
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        exp_val = ('<<ContextMenu>>', '<Key-Delete>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        e.set_menu_choices(('Option 1', 'Option 2', 'Option 3'))
        e.set_state('Option 2')
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementList, 'Option 2'))


if __name__ == '__main__':
    unittest.main()
