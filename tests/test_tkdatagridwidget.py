"""
This module provides unit tests for tkDataGridWidget class.
"""


# Standard
import unittest
import tkinter as tk
from math import isclose

# Local
from tkAppFramework.tkdatagridwidget import tkDGElementText, tkDataGridWidget, FieldType, tkDGElementBool, tkDGElementList, tkDGElementFieldHeader, FieldConfiguration
from tkAppFramework.tkdatagridwidget import DataGridUserAbilities
from tkAppFramework.datagridfigurewidget import ScatterPlotFieldsFigureTemplate
from tkAppFramework.datagriddemoapp import DemoUoMSysAdapter


class Test_DataGridUserAbilities(unittest.TestCase):
    def test_init(self):
        ua1 = DataGridUserAbilities()
        self.assertEqual(ua1._can_insert_field, False)
        self.assertEqual(ua1._can_delete_field , False)
        self.assertEqual(ua1._can_insert_record, False)
        self.assertEqual(ua1._can_delete_record, False)
        ua1 = DataGridUserAbilities(True, True, True, True)
        self.assertEqual(ua1._can_insert_field, True)
        self.assertEqual(ua1._can_delete_field , True)
        self.assertEqual(ua1._can_insert_record, True)
        self.assertEqual(ua1._can_delete_record, True)


class Test_tkDataGridWidget(unittest.TestCase):
    def setUp(self):
        self._root = tk.Tk()
        self._uom = DemoUoMSysAdapter()
        field_configurations = [FieldConfiguration('Editable Text Field',FieldType.TEXT,'editable'),
                                FieldConfiguration('Editable Bool Field',FieldType.BOOL,'editable'),
                                FieldConfiguration('Default List Field',FieldType.LIST,'editable'),
                                FieldConfiguration('Read Only Text Field',FieldType.TEXT,'read_only'),
                                FieldConfiguration('Read Only Number Field',FieldType.NUMBER,'read_only', None, 'gid_length', 'uid_meter', 'm')]
        self._dgw = tkDataGridWidget(self._root, fields_config=field_configurations, num_records=2, uom_adapter=self._uom)
        self._dgw.grid()
        # Create another data grid widget, but for this one, the fields are rows
        self._dgw_fr = tkDataGridWidget(self._root, fields_config=field_configurations, num_records=2, fields_are_cols=False, uom_adapter=self._uom)
        self._dgw_fr.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_init_num_records_property(self):
        self.assertEqual(self._dgw.num_records, 2)
        self.assertEqual(len(self._dgw._element_formats), 3)
        self.assertEqual(len(self._dgw._fields_config), 5)
        self.assertEqual(len(self._dgw._header_elements), 5)
        self.assertEqual(len(self._dgw._grid_elements), 5)
        self.assertEqual(len(self._dgw._grid_elements['Editable Text Field']), 2)
        self.assertEqual(len(self._dgw._subjects), 15)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][0])
        self.assertEqual(self._dgw.canvas, self._dgw._dg_canvas)
        self.assertEqual(self._dgw._fields_are_cols, True)
        self.assertTrue(isinstance(self._dgw._user_abilities, DataGridUserAbilities))
        self.assertEqual(self._dgw.uomAdapter, self._uom)
        self.assertIsNone(self._dgw._help_process)
        # tests method _draw_element_separator_lines()
        self.assertTrue(len(self._dgw.canvas.find_withtag('tag_element_separator_line')), 8)
        # tests method __setup_data_grid()
        self.assertEqual(len(self._dgw._wids), 15)

    def test_bindings(self):
        # Bindings on the tkDataGridWidget as a LabelFrame
        exp_val = '<Destroy>'
        self.assertEqual(len(self._dgw.bind()), 1)
        self.assertEqual(self._dgw.bind()[0], exp_val)
        # Bindings on all widgets
        exp_val = '<MouseWheel>'
        self.assertEqual(self._dgw.bind_all()[0], exp_val)

    def test_register_figure_template(self):
        ft = ScatterPlotFieldsFigureTemplate(x_label='X', y_label='Y', x_field='Read Only Number Field', y_fields=['Read Only Number Field'], symbols=['bo-'])
        self._dgw.register_figure_template('Y vs X', ft)
        self.assertEqual(len(self._dgw._fig_temps), 1)
        self.assertEqual(self._dgw._fig_temps['Y vs X'], ft)

    def test_onFocusIn_onFocusOut(self):
        self._dgw.onFocusOut(self._dgw._focused_element)
        self.assertEqual(self._dgw._focused_element, None)
        new_element = self._dgw._grid_elements['Editable Bool Field'][1]
        self._dgw.onFocusIn(new_element)
        self.assertEqual(self._dgw._focused_element, new_element)

    def test_onArrowKeys_fields_as_cols(self):
        # Test moving around in record elements with the arrow keys
        self._dgw.onKeyPressDown(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][1])
        self._dgw.onKeyPressRight(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Bool Field'][1])
        self._dgw.onKeyPressUp(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Bool Field'][0])
        self._dgw.onKeyPressLeft(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][0])
        # Test moving in, around, and our of header elements with the arrow keys
        self._dgw.onKeyPressUp(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._header_elements[0])
        self._dgw.onKeyPressRight(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._header_elements[1])
        self._dgw.onKeyPressLeft(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._header_elements[0])
        self._dgw.onKeyPressDown(None)
        self.assertEqual(self._dgw._focused_element, self._dgw._grid_elements['Editable Text Field'][0])

    def test_onArrowKeys_fields_as_rows(self):
        # Test moving around in record elements with the arrow keys
        self._dgw_fr.onKeyPressRight(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._grid_elements['Editable Text Field'][1])
        self._dgw_fr.onKeyPressDown(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._grid_elements['Editable Bool Field'][1])
        self._dgw_fr.onKeyPressLeft(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._grid_elements['Editable Bool Field'][0])
        self._dgw_fr.onKeyPressUp(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._grid_elements['Editable Text Field'][0])
        # Test moving in, around, and our of header elements with the arrow keys
        self._dgw_fr.onKeyPressLeft(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._header_elements[0])
        self._dgw_fr.onKeyPressDown(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._header_elements[1])
        self._dgw_fr.onKeyPressUp(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._header_elements[0])
        self._dgw_fr.onKeyPressRight(None)
        self.assertEqual(self._dgw_fr._focused_element, self._dgw_fr._grid_elements['Editable Text Field'][0])

    def test_get_field_unit_group(self):
        grp_id = self._dgw.get_field_unit_group('Read Only Number Field')
        self.assertEqual(grp_id, 'gid_length')
        
    def test_get_field_unitID(self):
        unit_id = self._dgw.get_field_unitID('Read Only Number Field')
        self.assertEqual(unit_id, 'uid_meter')

    def test_get_field_unit_name(self):
        unit_name = self._dgw.get_field_unit_name('Read Only Number Field')
        self.assertEqual(unit_name, 'm')
        
    def test_get_grid_element(self):
        ge = self._dgw._get_grid_element('Default List Field', 1)
        self.assertEqual(ge, self._dgw._grid_elements['Default List Field'][1])
        self.assertIsNone(self._dgw._get_grid_element('Nonexistent Field', 0))
        self.assertIsNone(self._dgw._get_grid_element('Default List Field', 100))
        # Test getting a header element
        he = self._dgw._get_grid_element('Default List Field', -1)
        self.assertEqual(he, self._dgw._header_elements[2])

    def test_get_grid_element_FieldType(self):
        geft = self._dgw.get_grid_element_FieldType('Editable Text Field', 1)
        self.assertEqual(geft, FieldType.TEXT)  
       
    def test_get_grid_element_value(self):
        ge = self._dgw._get_grid_element('Editable Text Field', 1)
        ge.set_state('Test Value')
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Value')

    def test_get_grid_element_value_display_units(self):
        ge = self._dgw._get_grid_element('Read Only Number Field', 1)
        ge.set_state(7.9)
        he = self._dgw._get_field_header_element('Read Only Number Field')
        he.set_units('uid_foot', 'ft')
        gev = self._dgw.get_grid_element_value_display_units('Read Only Number Field', 1)
        self.assertEqual(gev, 7.9/0.3048)

    def test_get_grid_element_FieldType(self):
        get = self._dgw.get_grid_element_FieldType('Editable Text Field', 1)
        self.assertEqual(get, FieldType.TEXT)
        get = self._dgw.get_grid_element_FieldType('Editable Bool Field', 1)
        self.assertEqual(get, FieldType.BOOL)
        get = self._dgw.get_grid_element_FieldType('Default List Field', 1)
        self.assertEqual(get, FieldType.LIST)
        get = self._dgw.get_grid_element_FieldType('Read Only Number Field', 1)
        self.assertEqual(get, FieldType.NUMBER)

    def test_get_grid_element_default_value(self):
        # Text element
        ge = self._dgw._get_grid_element('Editable Text Field', 1)
        ge.set_default_value('Test Default Value')
        gev = self._dgw.get_grid_element_default_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Default Value')
        # Number element
        ge = self._dgw._get_grid_element('Read Only Number Field', 1)
        ge.set_default_value(17.854)
        gev = self._dgw.get_grid_element_default_value('Read Only Number Field', 1)
        self.assertEqual(gev, 17.854)

    def test_set_grid_element_value(self):
        # Text element
        self._dgw.set_grid_element_value('Editable Text Field', 1, 'Test Value')
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Value')
        # Number element
        ge = self._dgw._get_grid_element('Read Only Number Field', 1)
        ge.set_state(17.854)
        gev = self._dgw.get_grid_element_value('Read Only Number Field', 1)
        self.assertEqual(gev, 17.854)

    def test_clear_grid_element_value(self):
        # Text element
        self._dgw.set_grid_element_value('Editable Text Field', 1, 'Test Value')
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Value')
        self._dgw.clear_grid_element_value('Editable Text Field', 1)
        gev = self._dgw.get_grid_element_value('Editable Text Field', 1)
        self.assertEqual(gev, '')
        # Number element
        self._dgw.set_grid_element_value('Read Only Number Field', 1, 17.854)
        gev = self._dgw.get_grid_element_value('Read Only Number Field', 1)
        self.assertEqual(gev, 17.854)
        self._dgw.clear_grid_element_value('Read Only Number Field', 1)
        gev = self._dgw.get_grid_element_value('Read Only Number Field', 1)
        self.assertEqual(gev, None)
        
    def test_set_grid_element_default_value(self):
        # Text element
        self._dgw.set_grid_element_default_value('Editable Text Field', 1, 'Test Default Value')
        gev = self._dgw.get_grid_element_default_value('Editable Text Field', 1)
        self.assertEqual(gev, 'Test Default Value')
        # Number element
        self._dgw.set_grid_element_default_value('Read Only Number Field', 1, 17.854)
        gev = self._dgw.get_grid_element_default_value('Read Only Number Field', 1)
        self.assertEqual(gev, 17.854)

    def test_set_grid_element_list_choices(self):
        self._dgw.set_grid_element_list_choices('Default List Field', 1, ('Test Option 1', 'Test Option 2'))
        gev = self._dgw.get_grid_element_value('Default List Field', 1)
        self.assertEqual(gev, 'Test Option 1')

    def test_get_element_coords(self):
        # Test getting the coordinates of a grid element that is part of a record
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        coords = self._dgw._get_element_coords(ge)
        self.assertTupleEqual(coords, ('Read Only Text Field', 1))
        # Test getting the cooridnates of a grid element that is a header element
        ge = self._dgw._get_grid_element('Read Only Text Field', -1)
        coords = self._dgw._get_element_coords(ge)
        self.assertTupleEqual(coords, ('Read Only Text Field', -1))

    def test_create_element_format(self):
        self._dgw.create_element_format()
        ef = self._dgw._element_formats['an_element_format']
        self.assertTupleEqual(ef, ('black', 'white', True, '#74BA00'))

    def test_create_context_menu(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        cm = self._dgw._create_context_menu(None, ge)
        # This is a weak test, in that it only tests that the method exectued with out exception and that it returns
        # an instance of the correct type. An improved test would be to inspect the returned instance in detail,
        # including what parts of the menu were disabled for a given element.
        self.assertIsInstance(cm, tk.Menu)

    def test_is_element_readonly(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(self._dgw._is_element_readonly(ge), True)
        ge = self._dgw._get_grid_element('Editable Text Field', 1)
        self.assertEqual(self._dgw._is_element_readonly(ge), False)

    def test_element_has_units(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(self._dgw._element_has_units(ge), False)
        ge = self._dgw._get_grid_element('Read Only Number Field', 1)
        self.assertEqual(self._dgw._element_has_units(ge), True)

    def test_deleteRecord(self):
        # Also tests _delete_record_elements()
        # Test deleting a record when it is a row of a data grid
        self.assertEqual(self._dgw.num_records, 2)
        self._dgw._deleteRecord(0)
        self.assertEqual(self._dgw.num_records, 1)
        # Test deleting a record when it is a column of a data grid
        self.assertEqual(self._dgw_fr.num_records, 2)
        self._dgw_fr._deleteRecord(0)
        self.assertEqual(self._dgw_fr.num_records, 1)

    def test_onDeleteColumnContextMenuOptionSelected(self):
        # When columns are records
        ge = self._dgw_fr._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(self._dgw_fr.num_records, 2)
        self._dgw_fr.onDeleteColumnContextMenuOptionSelected(ge)
        self.assertEqual(self._dgw_fr.num_records, 1)

    def test_onDeleteRowContextMenuOptionSelected(self):
        # When rows are records
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(self._dgw.num_records, 2)
        self._dgw.onDeleteRowContextMenuOptionSelected(ge)
        self.assertEqual(self._dgw.num_records, 1)

    def test_onInsertColumnContextMenuOptionSelected(self):
        # When columns are records
        ge = self._dgw_fr._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(self._dgw_fr.num_records, 2)
        self._dgw_fr.onInsertColumnContextMenuOptionSelected('left', ge)
        self.assertEqual(self._dgw_fr.num_records, 3)
        self._dgw_fr.onInsertColumnContextMenuOptionSelected('right', ge)
        self.assertEqual(self._dgw_fr.num_records, 4)

    def test_onInsertRowContextMenuOptionSelected(self):
        # When columns are records
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(self._dgw.num_records, 2)
        self._dgw.onInsertRowContextMenuOptionSelected('above', ge)
        self.assertEqual(self._dgw.num_records, 3)
        self._dgw.onInsertRowContextMenuOptionSelected('below', ge)
        self.assertEqual(self._dgw.num_records, 4)

    def test_insertRecordAfter(self):
        # Also tests _create_new_record().
        # Test inserting a record when it is a row of a data grid
        self.assertEqual(self._dgw.num_records, 2)
        self._dgw._insertRecordAfter(0)
        self.assertEqual(self._dgw.num_records, 3)
        # Test inserting a record when it is a column of a data grid
        self.assertEqual(self._dgw_fr.num_records, 2)
        self._dgw_fr._insertRecordAfter(0)
        self.assertEqual(self._dgw_fr.num_records, 3)

    def test_get_field_header_element(self):
        header_element_1 = self._dgw._header_elements[0]
        header_element_2 = self._dgw._get_field_header_element("Editable Text Field")
        self.assertEqual(header_element_1, header_element_2)

    def test_apply_element_format_to_one_element(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(ge.elementWidget['background'], 'cyan')
        self._dgw._apply_element_format_to_one_element('editable', ge)
        self.assertEqual(ge.elementWidget['background'], 'white')

    def test_apply_element_format_to_field_elements(self):
        ge = self._dgw._get_grid_element('Read Only Text Field', 1)
        self.assertEqual(ge.elementWidget['background'], 'cyan')
        self._dgw._apply_element_format_to_field_elements('editable', 'Read Only Text Field')
        self.assertEqual(ge.elementWidget['background'], 'white')

    def test_handle_element_updates(self):
        # FieldHeaderElementTextUpdateHint
        # Will set the state of a header element in a data grid, and test that the fieldName in the FieldConfiguration instance
        # has also changed.
        he = self._dgw._get_field_header_element("Editable Text Field")
        fc = self._dgw._fields_config[0]
        self.assertEqual(fc.fieldName, 'Editable Text Field')
        he.set_state("Writeable Text Field")
        self.assertEqual(fc.fieldName, 'Writeable Text Field')
        # FieldHeaderElementUnitsUpdateHint
        # Will set the units of a header element in the data grid, and test that the value in a record element for the field
        # has changed appropriately.
        he = self._dgw._get_field_header_element("Read Only Number Field")
        rec_elem = self._dgw._get_grid_element('Read Only Number Field', 0)
        rec_elem.set_state(1) # 1 meter
        self.assertEqual(float(rec_elem._element_value.get()), 1)
        he.set_units('uid_foot', 'ft')
        self.assertTrue(isclose(float(rec_elem._element_value.get()), 1/0.3048, rel_tol=1e-8))
        # RecordElementValueUpdateHint
        # Will set the value of a record element to its default value and test the background of the element
        ge = self._dgw._get_grid_element('Default List Field', 0)
        ge.set_menu_choices(('option 1', 'option 2', 'option 3'))
        ge.set_state('option 3')
        ge.set_default_value('option 2')
        self.assertEqual(ge.elementWidget['background'], 'white')
        ge.set_state('option 2')
        self.assertEqual(ge.elementWidget['background'], '#74BA00')
        # RecordElementDefaultValueUpdateHint
        # Will set the default value of a record element to a new value and test teh backgroud of the element
        ge.set_default_value('option 1')
        self.assertEqual(ge.elementWidget['background'], 'white')

    def test__draw_focus_rectangle(self):
        # A relatively weak test, but we will make sure the canvas ID associated with the tag "tag_focus_rectangle"
        # has changed.
        old_id = self._dgw.canvas.find_withtag('tag_focus_rectangle')
        ge = self._dgw._get_grid_element('Default List Field', 0)
        self._dgw._draw_focus_rectangle(ge)
        new_id = self._dgw.canvas.find_withtag('tag_focus_rectangle')
        self.assertNotEqual(old_id, new_id)

    def test_onDestroy(self):
        ge = self._dgw._get_grid_element('Editable Text Field', 0)
        self.assertEqual(len(ge._observers), 1)
        self._dgw.onDestroy(None)
        self.assertEqual(len(ge._observers), 0)


if __name__ == '__main__':
    unittest.main()
