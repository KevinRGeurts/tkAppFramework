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
        field_configurations = [('Editable Text Field',FieldType.TEXT,'editable'),
                                ('Editable Bool Field',FieldType.BOOL,'editable'),
                                ('Default List Field',FieldType.LIST,'default_value'),
                                ('Read Only Text Field',FieldType.TEXT,'read_only')]
        self._dgw = tkDataGridWidget(self._root, fields_config=field_configurations, num_records=2)
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_num_records_property(self):
        self.assertEqual(self._dgw.num_records, 2)
        self.assertEqual(len(self._dgw._element_formats), 4)
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
        
    def test_get_gird_element(self):
        ge = self._dgw.get_grid_element('Default List Field', 1)
        self.assertEqual(ge, self._dgw._grid_elements['Default List Field'][1])

    def test_get_element_coords(self):
        ge = self._dgw.get_grid_element('Read Only Text Field', 1)
        coords = self._dgw.get_element_coords(ge)
        self.assertTupleEqual(coords, ('Read Only Text Field', 1))

    def test_create_element_format(self):
        self._dgw.create_element_format()
        ef = self._dgw._element_formats['an_element_format']
        self.assertTupleEqual(ef, ('black', 'white', True))

    def test_onDestroy(self):
        ge = self._dgw.get_grid_element('Editable Text Field', 0)
        self._dgw.onDestroy(None)
        self.assertEqual(len(ge._observers), 0)



if __name__ == '__main__':
    unittest.main()
