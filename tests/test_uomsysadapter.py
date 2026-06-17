"""
This module provides unit tests for UoMSysAdapter class.
"""


# Standard imports
import unittest

# Local imports
from tkAppFramework.uomsysadapter import UoMSysAdapter


class Test_UoMSysAdapter(unittest.TestCase):
    def test_init(self):
        adapter = UoMSysAdapter('System of Units Object')
        self.assertEqual('System of Units Object', adapter._unit_sys)

    def test_get_unit_ids_of_unit_group(self):
        adapter = UoMSysAdapter('System of Units Object')
        self.assertRaises(NotImplementedError, adapter.get_unit_ids_of_unit_group, 'unit group id')

    def test_get_unit_names_for_unit(self):
        adapter = UoMSysAdapter('System of Units Object')
        self.assertRaises(NotImplementedError, adapter.get_unit_names_for_unit, 'unit id')

    def test_convert(self):
        adapter = UoMSysAdapter('System of Units Object')
        self.assertRaises(NotImplementedError, adapter.convert, 'from unit id', 'to unit id', 2.0)

    def test_get_base_unit_id_for_unit_group(self):
        adapter = UoMSysAdapter('System of Units Object')
        self.assertRaises(NotImplementedError, adapter.get_base_unit_id_for_unit_group, 'unit group id')
        

if __name__ == '__main__':
    unittest.main()
