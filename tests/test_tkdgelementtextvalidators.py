"""
This module provides unit tests for tkDGTextElemValidator class.
"""


# Standard
import unittest

# Local
from tkAppFramework.tkdgelementtextvalidators import tkDGTextElemValidator
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError


class Test_tkDGTextElemValidator(unittest.TestCase):
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

    def test_validate_entry_is_float(self):
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


if __name__ == '__main__':
    unittest.main()
