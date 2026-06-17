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
        fc = FieldConfiguration(name='A Field Name', field_type=FieldType.TEXT, field_format='A Field Format', validator=validator_func,
                                unit_group='A Unit Group ID', unit_id='A Unit ID', unit_name='A Unit Name')
        self.assertEqual('A Field Name', fc._field_name)
        self.assertEqual(FieldType.TEXT, fc._field_type)
        self.assertEqual('A Field Format', fc._field_format)
        self.assertEqual(validator_func, fc._field_validator)
        self.assertEqual('A Unit Group ID', fc._field_unit_group)
        self.assertEqual('A Unit ID', fc._field_unit_id)
        self.assertEqual('A Unit Name', fc._field_unit_name)

    def test_property_getters(self):
        def validator_func(val):
            pass
        fc = FieldConfiguration(name='A Field Name', field_type=FieldType.TEXT, field_format='A Field Format', validator=validator_func,
                                unit_group='A Unit Group ID', unit_id='A Unit ID', unit_name='A Unit Name')
        self.assertEqual('A Field Name', fc.fieldName)
        self.assertEqual(FieldType.TEXT, fc.fieldType)
        self.assertEqual('A Field Format', fc.fieldFormat)
        self.assertEqual(validator_func, fc.fieldValidator)
        self.assertEqual('A Unit Group ID', fc.fieldUnitGroup)
        self.assertEqual('A Unit ID', fc.fieldUnitID)
        self.assertEqual('A Unit Name', fc.fieldUnitName)

    def test_property_setters(self):
        fc = FieldConfiguration()
        fc.fieldUnitID='New Unit ID'
        fc.fieldUnitName='New Unit Name'
        self.assertEqual('New Unit ID', fc.fieldUnitID)
        self.assertEqual('New Unit Name', fc.fieldUnitName)
        

if __name__ == '__main__':
    unittest.main()
