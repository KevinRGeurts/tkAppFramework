"""
This module defines the tkDGTextElemValidators class. It defines static methods useful for validating text entries in
a tkDataGridWidget's tkDGElementText and tkDGElementNumber instances.

Exported Classes:
    tkDGTextElemValidator - A class that defines static methods useful for validating text entries in a tkDataGridWidget's
                            tkDGElementText and tkDGElementNumber instances.

Exported Exceptions:
    None    
 
Exported Functions:
    tkDGTextElemValidator.validate_entry_is_integer(min_value = None, max_value = None, proposed_entry = '')
    tkDGTextElemValidator.validate_entry_is_float(min_value = None, max_value = None, proposed_entry = '')
    tkDGTextElemValidator.validate_entry_is_string(min_length = None, max_length = None, proposed_entry = '')

Exceptions raised:
    tkDGElementTextInvalidEntryError - Raised when a proposed entry is not valid for a tkDGElementText instance.
                                       The error message will be informative to a user of the problem with the proposed entry.

"""


# standard library imports
import re

# local imports
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError
from tkAppFramework.tkdatagridwidget import tkDGElement


class tkDGTextElemValidator(object):
    """description of class"""

    def __init__(self):
        pass

    # Note: It makes no sense to "localize" integer values, since an integer in one unit of measure would seldom if ever be
    # an integer in another. The validator should probably only be used for unitless values.
    @staticmethod
    def validate_entry_is_integer(min_value = None, max_value = None, proposed_entry = ''):
        """
        Validate that the proposed entry is '' or an integer between min_value and max_value.
        If units of measure are relevant, then min_value and max_value should be provided in "base units".
        If the proposed entry is not valid, raise a tkDGElementTextInvalidEntryError, with an appropriate message to
        inform a user of the problem with the proposed entry.
        :parameter proposed_entry: The text entry to validate.
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
    def validate_entry_is_float(min_value = None, max_value = None, proposed_entry = '', element=None):
        """
        Validate that the proposed entry is '' or a floating point value between min_value and max_value.
        If the proposed entry is not valid, raise a tkDGElementTextInvalidEntryError, with an appropriate message to
        inform a user of the problem with the proposed entry.
        :parameter proposed_entry: The text entry to validate.
        :parameter element: The tkDGElement instance for which validation is being performed, as tkDGElement instance
            Note: This is optional. It should be included if the element's field has units of measure, so that
                  error messages can be "localized" to appropriate units.
        :return: (1) Float equivalent of text entry if the proposed entry is a valid floating point value,
                 (2) None if the proposed entry is '', or
                 (3) otherwise raise tkDGElementTextInvalidEntryError
        """
        assert isinstance(proposed_entry, str)
        # A blank entry is considered valid.
        if proposed_entry == '':
            return None
        # User regular expression to check if the proposed entry is a valid floating point value.
        txt_res = re.match(r'^[+-]?\d+$', proposed_entry) or \
                  re.match(r'^[+-]?((\d+\.\d*)|(\d*\.\d+))$', proposed_entry) or \
                  re.match(r'^[+-]?((\d+\.?\d*)|(\d*\.?\d+))[eE][+-]?\d+$', proposed_entry)
        if txt_res is not None:
            # Note that proposed_entry comes into the method in localized units, so float_res will also be in localized units
            float_res = float(txt_res[0])
            value_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(element, float_res)
            localized_max_val = tkDGTextElemValidator._localize_value(element, max_value)
            max_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(element, localized_max_val)
            localized_min_val = tkDGTextElemValidator._localize_value(element, min_value)
            min_str = tkDGTextElemValidator._combine_localized_value_with_units_into_string(element, localized_min_val)
            if (localized_min_val is None) or (float_res >= localized_min_val):
                    if (localized_max_val is None) or (float_res <= localized_max_val):
                        return float_res
                    else:
                        raise tkDGElementTextInvalidEntryError(f"Entry \'{value_str}\' must be a floating point value equal to or less than {max_str}.")
            else:
                raise tkDGElementTextInvalidEntryError(f"Entry \'{value_str}\' must be a floating point value equal to or greater than {min_str}.")
        else:
            raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' is not a valid floating point value.")

    @staticmethod
    def _localize_value(element, value):
        """
        A utility function to convert value into "localized" units of measure.
        :parameter value: The value to "localize", as float or int
        :parameter element: The tkDGElement instance to use for localization, as tkDGElement instance
        :return: Value in "localized" units, as float or int
            Notes: (1) Returns None if parameter value is None
                   (2) Returns value unchanged if element is None
        """
        if value is None:
            return None
        assert(isinstance(value, float) or isinstance(value, int))
        ret_val = value
        if element is not None:
            assert(isinstance(element, tkDGElement))
            # Convert value to localized units
            # Note: First master is the canvas, second master is the tkDataGridWidget
            owning_dgw = element.elementWidget.master.master
            (field_name, record_index) = owning_dgw._get_element_coords(element)
            localized_uid = owning_dgw.get_field_unitID(field_name)
            ugrpid = owning_dgw.get_field_unit_group(field_name)
            base_uid = owning_dgw.uomAdapter.get_base_unit_id_for_unit_group(ugrpid)
            ret_val = owning_dgw.uomAdapter.convert(from_unit_id=base_uid, to_unit_id=localized_uid, value=value)
        return ret_val

    @staticmethod
    def _combine_localized_value_with_units_into_string(element, value):
        """
        A utility function to create a string from value (assumed to already be in "localized" units) and
        "localized" unit name, of form f"{'{:.8G}'.format(value)} ({localized_unit_name})"
        :parameter value: A value already in localized units, as float or int
        :parameter element: The tkDGElement instance to use for localization, as tkDGElement instance
        :return: A string of form f"{'{:.8G}'.format(value)} ({localized_unit_name})", as string
            Note: (1) If element is None, the returned string will be of form '{:.8G}'.format(value)
                  (2) If value is None, then the returned string will be ''
        """
        if value is None:
            return ''
        assert(isinstance(value, float) or isinstance(value, int))
        localized_string = '{:.8G}'.format(value)
        if element is not None:
            assert(isinstance(element, tkDGElement))
            # Note: First master is the canvas, second master is the tkDataGridWidget
            owning_dgw = element.elementWidget.master.master
            (field_name, record_index) = owning_dgw._get_element_coords(element)
            localized_unit_name = owning_dgw.get_field_unit_name(field_name=field_name)
            localized_string = f"{localized_string} ({localized_unit_name})"
        return localized_string
        
    @staticmethod
    def validate_entry_is_string(min_length = None, max_length = None, proposed_entry = ''):
        """
        Validate that the proposed entry is '' or a string of length between min_length and max_length.
        If the proposed entry is not valid, raise a tkDGElementTextInvalidEntryError, with an appropriate message to
        inform a user of the problem with the proposed entry.
        :param proposed_entry: The text entry to validate.
        :return: (1) String equivalent of text entry if the proposed entry is a sting of valid length
                 (2) None if the proposed entry is '', or
                 (3) otherwise raise tkDGElementTextInvalidEntryError
        """
        assert isinstance(proposed_entry, str)
        # A blank entry is considered valid.
        if proposed_entry == '':
            return None
        txt_res = proposed_entry
        txt_length = len(txt_res)    
        if (min_length is None) or (txt_length >= min_length):
                if max_length is None or (txt_length <= max_length):
                    return txt_res
                else:
                    raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' must be a text string of length equal to or less than {max_length}.")
        else:
            raise tkDGElementTextInvalidEntryError(f"Entry \'{proposed_entry}\' must be a text string of length equal to or greater than {min_length}.")
