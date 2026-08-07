"""
This module provides unit tests for tkDGTextElemValidator class.
"""


# Standard
import unittest
import tkinter as tk

# Local
from tkAppFramework.tkdgelementtextvalidators import tkDGTextElemValidator
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError
from tkAppFramework.tkdatagridwidget import tkDataGridWidget, FieldConfiguration, FieldType
from tkAppFramework.datagriddemoapp import DemoUoMSysAdapter


class Test_tkDGTextElemValidator(unittest.TestCase):

    def setUp(self):
        self._root = tk.Tk()
        self.tf_config = FieldConfiguration('Text Field',FieldType.TEXT,'editable')
        self.nf_config = FieldConfiguration('Number Field',FieldType.NUMBER,'editable', None,
                                       'gid_length', 'uid_meter', 'm')
        field_configurations = [self.tf_config, self.nf_config]
        self._dgw = tkDataGridWidget(self._root, fields_config=field_configurations, num_records=2,
                                     uom_adapter=DemoUoMSysAdapter())
        self._dgw.grid()

    def tearDown(self):
        if self._root:
            self._root.destroy()

    def test_validate_entry_is_string(self):
        # Empty proposed_entry is valid and returns None.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_string(), None)
        # proposed_entry is valid, no min or max value specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_string(proposed_entry='Blah, blah, blah'), 'Blah, blah, blah')
        # proposed_entry is valid, with min and max lengths specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_string(min_length=15, max_length=16, proposed_entry='Blah, blah, blah'), 'Blah, blah, blah')
        # proposed_entry length is less than min_length.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_string(min_length=5, proposed_entry='Blah')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry 'Blah' must be a text string of length equal to or greater than 5.")
        # proposed_entry length is greater than max_length.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_string(max_length=9, proposed_entry='Blah, blah')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry 'Blah, blah' must be a text string of length equal to or less than 9.")

    def test_localize_value(self):
        ne = self._dgw._get_grid_element('Number Field', 0)
        # Test that None is returned if None is passed in as value
        value = tkDGTextElemValidator._localize_value(ne, None)
        self.assertEqual(value, None)
        # Test that value is returned unchanged if element is None
        value = tkDGTextElemValidator._localize_value(None, 24.56)
        self.assertEqual(value, 24.56)
        # Test return of value in base units
        value = tkDGTextElemValidator._localize_value(ne, 1.0)
        self.assertEqual(value, 1.0)
        # Test return of value in localized units
        self.nf_config.fieldUnitID = 'uid_foot'
        self.nf_config.fieldUnitName = 'ft'
        value = tkDGTextElemValidator._localize_value(ne, 1.0)
        self.assertEqual(value, 3.280839895013123)

    def test_combine_localized_value_with_units_into_string(self):
        ne = self._dgw._get_grid_element('Number Field', 0)
        # Test that '' is returned if None is passed in as value
        value_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(ne, None)
        self.assertEqual(value_str, '')
        # Test that value is not  localized if element is None
        value_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(None, 24.56)
        self.assertEqual(value_str, '{:.8G}'.format(24.56))
        # Test return of value in base units
        value_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(ne, 1.0)
        self.assertEqual(value_str, f"{'{:.8G}'.format(1.0)} (m)")
        # Test return of value in localized units
        self.nf_config.fieldUnitID = 'uid_foot'
        self.nf_config.fieldUnitName = 'ft'
        value_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(ne, 1.0)
        self.assertEqual(value_str, f"{'{:.8G}'.format(1.0)} (ft)")

    def test_validate_entry_is_float_units(self):
        ne = self._dgw._get_grid_element('Number Field', 0)
        self.nf_config.fieldUnitID = 'uid_foot'
        self.nf_config.fieldUnitName = 'ft'
        # Empty proposed_entry is valid and returns None.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_float(element=ne), None)
        # proposed_entry is valid, no min or max value specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_float(proposed_entry='+1.7e-4', element=ne), 1.7e-4)
        # proposed_entry is valid, with min and max values specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_float(min_value=1.0, max_value=3.0, proposed_entry='6.0', element=ne), 6.0)
        # proposed_entry is not a valid float.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_float(proposed_entry='1.7e-4.5', element=ne)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '1.7e-4.5' is not a valid floating point value.")
        # proposed_entry is less than min_value.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_float(min_value=2.0, proposed_entry='1.0', element=ne)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '1 (ft)' must be a floating point value equal to or greater than 6.5616798 (ft).")
        # proposed_entry is greater than max_value.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_float(max_value=1.0, proposed_entry='6.0', element=ne)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '6 (ft)' must be a floating point value equal to or less than 3.2808399 (ft).")

    def test_validate_entry_is_float_no_units(self):
        # Empty proposed_entry is valid and returns None.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_float(), None)
        # proposed_entry is valid, no min or max value specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_float(proposed_entry='+1.7e-4'), 1.7e-4)
        # proposed_entry is valid, with min and max values specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_float(min_value=9, max_value=11, proposed_entry='10.5'), 10.5)
        # proposed_entry is not a valid float.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_float(proposed_entry='1.7e-4.5')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '1.7e-4.5' is not a valid floating point value.")
        # proposed_entry is less than min_value.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_float(min_value=11, proposed_entry='10.5')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '10.5' must be a floating point value equal to or greater than 11.")
        # proposed_entry is greater than max_value.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_float(max_value=9, proposed_entry='10.5')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '10.5' must be a floating point value equal to or less than 9.")

    def test_validate_entry_is_integer(self):
        # Empty proposed_entry is valid and returns None.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_integer(), None)
        # proposed_entry is valid, no min or max value specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_integer(proposed_entry='10'), 10)
        # proposed_entry is valid, with min and max values specified.
        self.assertEqual(tkDGTextElemValidator.validate_entry_is_integer(min_value=9, max_value=11, proposed_entry='10'), 10)
        # proposed_entry is not a valid integer.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_integer(proposed_entry='abc')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry 'abc' is not a valid integer.")
        # proposed_entry is less than min_value.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_integer(min_value=11, proposed_entry='10')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '10' must be an integer equal to or greater than 11.")
        # proposed_entry is greater than max_value.
        with self.assertRaises(tkDGElementTextInvalidEntryError) as cm:
            tkDGTextElemValidator.validate_entry_is_integer(max_value=9, proposed_entry='10')
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "Entry '10' must be an integer equal to or less than 9.")


if __name__ == '__main__':
    unittest.main()
