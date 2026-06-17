"""
This module provides unit tests for FieldConfiguration class.
"""


# Standard imports
import unittest

# Local imports
from tkAppFramework.tkdatagridwidget import FieldConfiguration, FieldType


class Test_FieldConfiguration(unittest.TestCase):
    def test_init(self):
        def validator_func(val):
            pass
        fc = FieldConfiguration(name='A Field Name', field_type=FieldType.TEXT, field_format='A Field Format', validator=validator_func, unit_group='A Unit Group ID')
        self.assertEqual('A Field Name', fc._field_name)
        self.assertEqual(FieldType.TEXT, fc._field_type)
        self.assertEqual('A Field Format', fc._field_format)
        self.assertEqual(validator_func, fc._field_validator)
        self.assertEqual('A Unit Group ID', fc._field_unit_group)

    def test_property_getters(self):
        def validator_func(val):
            pass
        fc = FieldConfiguration(name='A Field Name', field_type=FieldType.TEXT, field_format='A Field Format', validator=validator_func, unit_group='A Unit Group ID')
        self.assertEqual('A Field Name', fc.fieldName)
        self.assertEqual(FieldType.TEXT, fc.fieldType)
        self.assertEqual('A Field Format', fc.fieldFormat)
        self.assertEqual(validator_func, fc.fieldValidator)
        self.assertEqual('A Unit Group ID', fc.fieldUnitGroup)
        

if __name__ == '__main__':
    unittest.main()
