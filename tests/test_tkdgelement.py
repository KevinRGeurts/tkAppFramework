"""
This module provides unit tests for tkDGElement class and children.
"""


# Standard
from dataclasses import Field
import unittest
import tkinter as tk
from math import isclose

# Local
from tkAppFramework.tkdatagridwidget import tkDGElement, tkDGElementText, tkDataGridWidget, FieldType, tkDGElementBool, tkDGElementList, tkDGElementFieldHeader, tkDGElementNumber, FieldConfiguration
from tkAppFramework.ObserverPatternBase import Observer
from tkAppFramework.datagriddemoapp import DemoUoMSysAdapter


class Test_tkDGElement(unittest.TestCase):
    def test_init(self):
        obs = Observer()
        self.assertRaises(NotImplementedError, tkDGElement, obs)


class Test_tkDGElementText(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        fcs = [FieldConfiguration('A Text Field', FieldType.TEXT, 'editable', None, None, None, ''),
               FieldConfiguration('Another Text Field', FieldType.TEXT, 'editable', None, None, None, '')]
        self._dgw = tkDataGridWidget(self._root, fields_config=fcs, num_records=2)
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_elementWidget_prop_get_state(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.Entry)
        self.assertIsInstance(e._element_value, tk.StringVar)
        self.assertEqual(e.canvasID, 9)
        self.assertTupleEqual(e.get_state(),(tkDGElementText, ''))

    def test_set_get_default_value(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_default_value('Default Text')
        self.assertEqual(e.get_default_value(), 'Default Text')

    def test_restoreDefaultValue_onF3(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_default_value('Default Text')
        e.set_state('Not Default Text')
        e._restoreDefaultValue()
        self.assertEqual(e.get_state()[1], 'Default Text')
        e.set_state('Not Default Text')
        e.onKeyPressF3(None)
        self.assertEqual(e.get_state()[1], 'Default Text')

    def test_arrowKeys(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertEqual(self._dgw._focused_element, e)
        e.onKeyPressDown(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._get_grid_element('A Text Field', 1))
        e.onKeyPressUp(None)
        self.assertEqual(self._dgw._focused_element, e)
        e.onKeyPressRight(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._get_grid_element('Another Text Field', 0))
        e.onKeyPressLeft(None)
        self.assertEqual(self._dgw._focused_element, e)

    def test_OnFocusIn_OnFocusOut(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertEqual(self._dgw._focused_element, e)
        e.onFocusOut(None)
        self.assertIsNone(self._dgw._focused_element)
        e.onFocusIn(None)
        self.assertEqual(self._dgw._focused_element, e)
        
    def test_set_get_state(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_state('1')
        self.assertTupleEqual(e.get_state(), (tkDGElementText, '1'))

    def test_OnEntryChanged(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        # Setting the element's widget's control variable will call OnEntryChanged
        e._element_value.set('abc')
        self.assertTupleEqual(e.get_state(), (tkDGElementText, 'abc'))

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], 'readonly')
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        exp_val = ('<Key-KP_Enter>', '<Key-Return>', '<Leave>', '<Enter>', '<<ContextMenu>>', '<Key-F3>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_state('Some Text')
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementText, ''))

    def test_getToolTipText(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        e.set_state('Some Text')
        e.set_default_value('Default Text')
        self.assertEqual(e._getToolTipText(), 'Value: Some Text\nDefault: Default Text')

    def test_onElementWidgetEnter_Leave(self):
        e = self._dgw._get_grid_element('A Text Field', 0)
        self.assertIsNone(e._after_id)
        e.onElementWidgetEnter(None)
        self.assertIsNotNone(e._after_id)
        e.onElementWidgetLeave(None)
        self.assertIsNone(e._after_id)


class Test_tkDGElementNumber(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        _uom = DemoUoMSysAdapter()
        fcs = [FieldConfiguration('Unit Number Field', FieldType.NUMBER, 'editable', None, 'gid_length', 'uid_meter', 'm'),
               FieldConfiguration('No Unit Number Field', FieldType.NUMBER, 'editable', None, None, None, '')]
        self._dgw = tkDataGridWidget(self._root, fields_config=fcs, num_records=1, uom_adapter=_uom)
        self._dgw.grid()
        self._units_header_element = self._dgw._header_elements[0]  # Get the header element for the first field.

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_prop_get_state(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.Entry)
        self.assertIsInstance(e._element_value, tk.StringVar)
        self.assertEqual(e.canvasID, 8)
        self.assertTupleEqual(e.get_state(),(tkDGElementNumber, None))

    def test_set_get_default_value(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        e.set_default_value(5.7)
        self.assertEqual(e.get_default_value(), 5.7)

    def test_restoreDefaultValue(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        # No default value to restore
        e.set_state(3.2)
        self.assertEqual(e.get_state()[1], 3.2)
        e._restoreDefaultValue()
        self.assertEqual(e.get_state()[1], 3.2)
        # Default value to restore
        e.set_default_value(5.7)
        e.set_state(3.2)
        self.assertEqual(e.get_state()[1], 3.2)
        e._restoreDefaultValue()
        self.assertEqual(e.get_state()[1], 5.7)

    def test_onKeyPressF3(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        e.set_default_value(5.7)
        e.set_state(3.2)
        self.assertEqual(e.get_state()[1], 3.2)
        e.onKeyPressF3(None)
        self.assertEqual(e.get_state()[1], 5.7)
        
    def test_set_get_state(self):
        e = self._dgw._get_grid_element('No Unit Number Field', 0)
        e.set_state(1.6)
        self.assertTupleEqual(e.get_state(), (tkDGElementNumber, 1.6))
        self.assertEqual(e._element_value.get(), '1.6')
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        he = self._units_header_element
        he.set_units('uid_foot','ft')
        e.set_state(1.6)
        print(f"state: {e.get_state()[1]}")
        self.assertTrue(isclose(e.get_state()[1], 1.6, rel_tol=1e-8))
        self.assertTrue(isclose(float(e._element_value.get()), 1.6/0.3048, rel_tol=1e-8))

    def test_get_value_in_display_units(self):
        e = self._dgw._get_grid_element('No Unit Number Field', 0)
        e.set_state(1.6)
        self.assertTupleEqual(e.get_value_in_display_units(), (1.6, ''))
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        he = self._units_header_element
        he.set_units('uid_foot','ft')
        e.set_state(1.6)
        (vdu, du) = e.get_value_in_display_units()
        self.assertTrue(isclose(vdu, 1.6/0.3048, rel_tol=1e-8))
        self.assertEqual(du, 'ft')

    def test_get_default_value_in_display_units(self):
        e = self._dgw._get_grid_element('No Unit Number Field', 0)
        e.set_default_value(1.6)
        self.assertTupleEqual(e.get_default_value_in_display_units(), (1.6, ''))
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        he = self._units_header_element
        he.set_units('uid_foot','ft')
        e.set_default_value(1.6)
        (vdu, du) = e.get_default_value_in_display_units()
        self.assertTrue(isclose(vdu, 1.6/0.3048, rel_tol=1e-8))
        self.assertEqual(du, 'ft')

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], 'readonly')
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        exp_val = ('<Key-KP_Enter>', '<Key-Return>', '<Leave>', '<Enter>', '<<ContextMenu>>', '<Key-F3>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        e.set_state(9.23)
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementNumber, None))
        self.assertEqual(e._element_value.get(), '')

    def test_fuzzy_compare(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        self.assertEqual(e._fuzzy_compare(None, None), True)
        self.assertEqual(e._fuzzy_compare(None, 1.0), False)
        self.assertEqual(e._fuzzy_compare(1.0, None), False)
        self.assertEqual(e._fuzzy_compare(1.0, 2.0), False)
        self.assertEqual(e._fuzzy_compare(1.0, 1.0 + 2e-8), False)
        self.assertEqual(e._fuzzy_compare(1.0, 1.0 + 1e-8), True)

    def test_format_value(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        self.assertEqual(e._format_value(1.0), '1')
        self.assertEqual(e._format_value(1.23456789123), '1.2345679')
        self.assertEqual(e._format_value(123456789123), '1.2345679E+11')

    def test_getToolTipText(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        e.set_state(9.23)
        e.set_default_value(5.7)
        self.assertEqual(e._getToolTipText(), 'Value: 9.23 (m)\nDefault: 5.7 (m)')
        e = self._dgw._get_grid_element('No Unit Number Field', 0)
        e.set_state(9.23)
        e.set_default_value(5.7)
        self.assertEqual(e._getToolTipText(), 'Value: 9.23\nDefault: 5.7')

    def test_OnEntryChanged(self):
        e = self._dgw._get_grid_element('Unit Number Field', 0)
        he = self._units_header_element
        he.set_units('uid_foot','ft')
        e._element_value.set('9.23')
        e.OnEntryChanged(e.canvasID)
        self.assertEqual(e.get_state()[1], 9.23*0.3048)


class Test_tkDGElementFieldHeader(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        _uom = DemoUoMSysAdapter()
        fcs = [FieldConfiguration('Field With Units', FieldType.TEXT, 'editable', None, 'gid_length', 'uid_meter', 'm'),
               FieldConfiguration('Field No Units', FieldType.TEXT, 'editable', None, None, None, '')]
        self._dgw = tkDataGridWidget(self._root, fields_config=fcs, num_records=1, uom_adapter=_uom)
        self._dgw.grid()
        self._units_header_element = self._dgw._header_elements[0]  # Get the header element for the first field.
        self._no_units_header_element = self._dgw._header_elements[1]  # Get the header element for the second field.

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_canvasID_prop_get_state(self):
        e = self._units_header_element 
        self.assertEqual(e._observers[0], self._dgw)
        self.assertIsInstance(e.elementWidget, tk.Entry)
        self.assertIsInstance(e._element_value, tk.StringVar)
        self.assertEqual(e.canvasID, 7)
        self.assertTupleEqual(e.get_state(),(tkDGElementFieldHeader, 'Field With Units (m)'))
        self.assertEqual(e._raw_state, 'Field With Units')

    def test_set_default_value(self):
        e = self._units_header_element 
        self.assertIsNone(e.get_default_value())
        e.set_default_value()
        self.assertIsNone(e.get_default_value())
        self.assertRaises(AssertionError, e.set_default_value, 'Default Value That Will Not Be Set')

    def test_set_state(self):
        e = self._units_header_element
        e.set_state('Units Field Name')
        self.assertTupleEqual(e.get_state(), (tkDGElementFieldHeader, 'Units Field Name (m)'))
        self.assertEqual(e._raw_state, 'Units Field Name')
        e = self._no_units_header_element
        e.set_state('No Units Field Name')
        self.assertTupleEqual(e.get_state(), (tkDGElementFieldHeader, 'No Units Field Name'))
        self.assertEqual(e._raw_state, 'No Units Field Name')

    def test_disable_element_elementWidget_prop(self):
        e = self._units_header_element
        self.assertEqual(e.elementWidget['state'], 'readonly')
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], 'readonly')

    def test_bindings(self):
        e = self._units_header_element
        exp_val = ('<Double-Button-1>', '<Leave>', '<Enter>', '<<ContextMenu>>', '<Key-F3>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._units_header_element
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementFieldHeader, ' (m)'))
        self.assertEqual(e._raw_state, '')
        e = self._no_units_header_element
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementFieldHeader, ''))
        self.assertEqual(e._raw_state, '')

    def test_set_units(self):
        e = self._units_header_element
        e.set_units(unit_id='a_unit_id', unit_name='a unit name')
        self.assertTupleEqual(e.get_state(), (tkDGElementFieldHeader, 'Field With Units (a unit name)'))
        self.assertEqual(e._raw_state, 'Field With Units')

    def test_getToolTipText(self):
        e = self._units_header_element
        self.assertEqual(e._getToolTipText(), 'Value: Field With Units (m)')
        e = self._no_units_header_element
        self.assertEqual(e._getToolTipText(), 'Value: Field No Units')

class Test_tkDGElementBool(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._dgw = tkDataGridWidget(self._root, fields_config=[FieldConfiguration('A Boolean Field', FieldType.BOOL, 'editable', None, None, None, '')], num_records=1)
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
        self.assertTupleEqual(e.get_state(),(tkDGElementBool, False))

    def test_onCheckbuttonClicked(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        self.assertTupleEqual(e.get_state(), (tkDGElementBool, False))
        # Manually set the control variable to "checked"
        e._element_value.set(1)
        # Because onCheckbuttonClicked just picks up the current value of the control variable and calls set_state()
        e.onCheckbuttonClicked(e.canvasID)
        self.assertTupleEqual(e.get_state(), (tkDGElementBool, True))

    def test_set_state(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        e.set_state(True)
        self.assertTupleEqual(e.get_state(), (tkDGElementBool, True))

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], tk.DISABLED)
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        exp_val = ('<Leave>', '<Enter>', '<<ContextMenu>>', '<Key-F3>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        e.set_state(True)
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementBool, False))

    def test_getToolTipText(self):
        e = self._dgw._get_grid_element('A Boolean Field', 0)
        self.assertEqual(e._getToolTipText(), 'Value: False')


class Test_tkDGElementList(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._dgw = tkDataGridWidget(self._root, fields_config=[FieldConfiguration('A List Field', FieldType.LIST, 'editable', None, None, None, '')], num_records=1)
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

    def test_onOptionSelected(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        e.set_menu_choices(('Option 1', 'Option 2', 'Option 3'))
        e.onOptionSelected(e.canvasID, 'Option 3')
        self.assertTupleEqual(e.get_state(), (tkDGElementList, 'Option 3'))

    def test_disable_element_elementWidget_prop(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)
        e.disable_element(True)
        self.assertEqual(e.elementWidget['state'], tk.DISABLED)
        e.disable_element(False)
        self.assertEqual(e.elementWidget['state'], tk.NORMAL)

    def test_bindings(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        exp_val = ('<Leave>', '<Enter>', '<<ContextMenu>>', '<Key-F3>', '<Key-Left>', '<Key-Right>', '<Key-Down>', '<Key-Up>', '<FocusOut>', '<FocusIn>')
        self.assertTupleEqual(e.elementWidget.bind(), exp_val)

    def test_clear_element_value(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        e.set_menu_choices(('Option 1', 'Option 2', 'Option 3'))
        e.set_state('Option 2')
        # clear_element_value() does nothing to a tkDGElementList
        e.clear_element_value()
        self.assertTupleEqual(e.get_state(), (tkDGElementList, 'Option 2'))

    def test_set_menu_choices(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        e.set_menu_choices(('Option 1', 'Option 2', 'Option 3'))
        e.set_state('Option 2')
        self.assertTupleEqual(e.get_state(), (tkDGElementList, 'Option 2'))
        e.set_menu_choices(('Option 4', 'Option 5', 'Option 6'))
        self.assertTupleEqual(e.get_state(), (tkDGElementList, 'Option 4'))

    def test_getToolTipText(self):
        e = self._dgw._get_grid_element('A List Field', 0)
        e.set_menu_choices(('Option 1', 'Option 2', 'Option 3'))
        e.set_state('Option 2')
        e.set_default_value('Option 3')
        self.assertEqual(e._getToolTipText(), 'Value: Option 2\nDefault: Option 3')


if __name__ == '__main__':
    unittest.main()
