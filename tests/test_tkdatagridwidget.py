"""
This module provides unit tests for tkDataGridWidget class.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.tkdatagridwidget import tkDGElementText, tkDataGridWidget, FieldType, tkDGElementBool, tkDGElementList, tkDGElementFieldHeader


class Test_tkDataGridWidget(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        field_configurations = [('Editable Text Field',FieldType.TEXT,'editable', None),
                                ('Editable Bool Field',FieldType.BOOL,'editable', None),
                                ('Default List Field',FieldType.LIST,'editable', None),
                                ('Read Only Text Field',FieldType.TEXT,'read_only', None)]
        self._dgw = tkDataGridWidget(self._root, fields_config=field_configurations, num_records=2)
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_num_records_property(self):
        self.assertEqual(self._dgw.num_records, 2)
        self.assertEqual(len(self._dgw._element_formats), 3)
        self.assertEqual(len(self._dgw._fields_config), 4)
        self.assertEqual(len(self._dgw._header_elements), 4)
        self.assertEqual(len(self._dgw._grid_elements), 4)
        self.assertEqual(len(self._dgw._grid_elements['Editable Text Field']), 2)
        self.assertEqual(len(self._dgw._wids), 12)
        self.assertEqual(len(self._dgw._subjects), 12)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][0])
        self.assertEqual(self._dgw.canvas, self._dgw._dg_canvas)

    def test_onFocusIn_onFocusOut(self):
        self._dgw.onFocusOut(self._dgw._focused_element)
        self.assertEqual(self._dgw._focused_element, None)
        new_element = self._dgw._grid_elements['Editable Bool Field'][1]
        self._dgw.onFocusIn(new_element)
        self.assertEqual(self._dgw._focused_element, new_element)

    def test_onArrowKeys(self):
        self._dgw.onKeyPressDown(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][1])
        self._dgw.onKeyPressRight(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Bool Field'][1])
        self._dgw.onKeyPressUp(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Bool Field'][0])
        self._dgw.onKeyPressLeft(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][0])
        
    def test_get_grid_element(self):
        ge = self._dgw._get_grid_element('Default List Field', 1)
        self.assertEqual(ge, self._dgw._grid_elements['Default List Field'][1])
        self.assertIsNone(self._dgw._get_grid_element('Nonexistent Field', 0))
        self.assertIsNone(self._dgw._get_grid_element('Default List Field', 100))

    def test_get_grid_element_FieldType(self):
        geft = self._dgw.get_grid_element_FieldType('Editable Text Field', 1)
        self.assertEqual(geft, FieldType.TEXT)  
       
    def test_get_grid_element_value(self):
        ge = self._dgw._get_grid_element('Editable Text Field', 1)
        ge.set_state('Test Value')
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Value')

    def test_get_grid_element_default_value(self):
        ge = self._dgw._get_grid_element('Editable Text Field', 1)
        ge.set_default_value('Test Default Value')
        gev = self._dgw.get_grid_element_default_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Default Value')

    def test_set_grid_element_value(self):
        self._dgw.set_grid_element_value('Editable Text Field', 1, 'Test Value')
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Value')

    def test_clear_grid_element_value(self):
        self._dgw.set_grid_element_value('Editable Text Field', 1, 'Test Value')
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Value')
        self._dgw.clear_grid_element_value('Editable Text Field', 1)
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, '')
        
    def test_set_grid_element_default_value(self):
        self._dgw.set_grid_element_default_value('Editable Text Field', 1, 'Test Default Value')
        gev = self._dgw.get_grid_element_default_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Default Value')

    def test_set_grid_element_list_choices(self):
        self._dgw.set_grid_element_list_choices('Default List Field', 1, ('Test Option 1', 'Test Option 2'))
        gev = self._dgw.get_grid_element_value('Default List Field', 1)
        self.assertEqual(gev, 'Test Option 1')

    def test_get_element_coords(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        coords = self._dgw._get_element_coords(ge)
        self.assertTupleEqual(coords, ('Read Only Text Field', 1))

    def test_modified_grid_element_coords(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self._dgw._modified_element = ge
        coords = self._dgw.get_modified_grid_element_location()
        self.assertTupleEqual(coords, ('Read Only Text Field', 1))

    def test_create_element_format(self):
        self._dgw.create_element_format()
        ef = self._dgw._element_formats['an_element_format']
        self.assertTupleEqual(ef, ('black', 'white', True, '#74BA00'))

    def test_onDestroy(self):
        ge = self._dgw._get_grid_element('Editable Text Field', 0)
        self.assertEqual(len(ge._observers), 1)
        self._dgw.onDestroy(None)
        self.assertEqual(len(ge._observers), 0)


if __name__ == '__main__':
    unittest.main()
