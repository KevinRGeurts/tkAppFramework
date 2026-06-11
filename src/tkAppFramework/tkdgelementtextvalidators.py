"""
This module defines the tkDGTextElemValidators class. It defines static methods useful for validating text entries in
a tkDataGridWidget's tkDGElementText instances.

Exported Classes:
    tkDGTextElemValidator - A class that defines static methods useful for validating text entries in a tkDataGridWidget's
                            tkDGElementText instances.

Exported Exceptions:
    None    
 
Exported Functions:
    tkDGTextElemValidator.validate_entry_is_integer(min_value = None, max_value = None, proposed_entry = '')
    tkDGTextElemValidator.validate_entry_is_float(min_value = None, max_value = None, proposed_entry = '')

Exceptions raised:
    tkDGElementTextInvalidEntryError - Raised when a proposed entry is not valid for a tkDGElementText instance.
                                       The error message will be informative to a user of the problem with the proposed entry.

"""


# standard library imports
import re

# local imports
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError


class tkDGTextElemValidator(object):
    """description of class"""

    def __init__(self):
        pass

    @staticmethod
    def validate_entry_is_integer(min_value = None, max_value = None, proposed_entry = ''):
        """
        Validate that the proposed entry is '' or an integer between min_value and max_value.
        If the proposed entry is not valid, raise a tkDGElementTextInvalidEntryError, with an appropriate message to
        inform a user of the problem with the proposed entry.
        :param proposed_entry: The text entry to validate.
        :return: (1) Integer equivalent of text entry if the proposed entry is a valid integer,
                 (2) None if the proposed entry is '', or
                 (3) otherwise raise tkDGElementTextInvalidEntryError
        """
        assert isinstance(proposed_entry, str)
        # A blank entry is considered valid.
        if proposed_entry == '':
            return None
        int_res = None
        # User regular expression to check if the proposed entry is a valid integer.
        txt_res = re.match(r'^[+-]?\d+$', proposed_entry)
        if txt_res is not None:
            int_res = int(txt_res[0])    
            if (min_value is None) or (int_res >= min_value):
                    if max_value is None or (int_res <= max_value):
                        return int_res
                    else:
                        raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' must be an integer equal to or less than {max_value}.")
            else:
                raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' must be an integer equal to or greater than {min_value}.")
        else:
            raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' is not a valid integer.")

    @staticmethod
    def validate_entry_is_float(min_value = None, max_value = None, proposed_entry = ''):
        """
        Validate that the proposed entry is '' or a floating point value between min_value and max_value.
        If the proposed entry is not valid, raise a tkDGElementTextInvalidEntryError, with an appropriate message to
        inform a user of the problem with the proposed entry.
        :param proposed_entry: The text entry to validate.
        :return: (1) Float equivalent of text entry if the proposed entry is a valid floating point value,
                 (2) None if the proposed entry is '', or
                 (3) otherwise raise tkDGElementTextInvalidEntryError
        """
        assert isinstance(proposed_entry, str)
        # A blank entry is considered valid.
        if proposed_entry == '':
            return None
        int_res = None
        # User regular expression to check if the proposed entry is a valid floating point value.
        txt_res = re.match(r'^[+-]?\d+$', proposed_entry) or \
                  re.match(r'^[+-]?((\d+\.\d*)|(\d*\.\d+))$', proposed_entry) or \
                  re.match(r'^[+-]?((\d+\.?\d*)|(\d*\.?\d+))e[+-]?\d+$', proposed_entry)
        if txt_res is not None:
            float_res = float(txt_res[0])    
            if (min_value is None) or (float_res >= min_value):
                    if max_value is None or (float_res <= max_value):
                        return float_res
                    else:
                        raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' must be a floating point value equal to or less than {max_value}.")
            else:
                raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' must be a floating point value equal to or greater than {min_value}.")
        else:
            raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' is not a valid floating point value.")

