"""
This module provides the UoMSysAdapter class that follows the Adapter design patter to adapt a Units of Measurement System (UoMSys)
to a common interface expected by tkDataGridWidget. It is an Object Adaptater that relies on composition to adapt a UoMSys to the
expected interface.

Exported Classes:
    UoMSysAdapter -- A class that follows the Adapter design patter to adapt a Units of Measurement System (UoMSys) to a common
                     interface expected by tkDataGridWidget. It is an Object Adaptater that relies on composition to adapt
                     a UoMSys to the expected interface.

Exported Exceptions:
    None
 
Exported Functions:
    None
"""

# standard library imports


# local imports


class UoMSysAdapter(object):
    """
    This class follows the Adapter design patter to adapt a Units of Measurement System (UoMSys) to a common interface
    expected to tkDataGridWidget. It is an Object Adaptater that relys on composition to adapt a UoMSys to the expected interface.
    """
    def __init__(self, unit_sys=None):
        """
        :parameter unit_sys: The Units of Measurement System (UoMSys) to adapt to the expected interface.
        """
        self._unit_sys = unit_sys

    def get_unit_ids_of_unit_group(self, unit_group_id):
        """
        Get the unit IDs of the units in the unit group specified by unit_group_id.
        :param unit_group_id: The ID of the unit group to get the unit IDs of, as Any
        :return: A list of unit IDs of the units in the specified unit group, as [Any]
        """
        # Implement this method to return the appropriate unit IDs based on the provided unit_group_id
        raise NotImplementedError
        return []

    def get_unit_names_for_unit(self, unit_id):
        """
        Get the unit names (synonyms) of the unit specified by unit_id.
        :param unit_id: The ID of the unit to get the synonyms for, as Any
        :return: A list of synonyms of the unit with the specified unit ID, as [strings]
        """
        # Implement this method to return the appropriate unit synonyms based on the provided unit_id
        raise NotImplementedError
        return []

    def convert(self, from_unit_id, to_unit_id, value):
        """
        Convert value from the unit specified by from_unit_id to the unit specified by to_unit_id.
        :parameter from_unit_id: The ID of the unit to convert from, as Any
        :parameter to_unit_id: The ID of the unit to convert to, as Any
        :parameter value: The value to convert, as float.
        :return: The converted value, as float. 
        """
        # Implement this method to return value converted to new units.
        raise NotImplementedError
        return 0.0

    def get_base_unit_id_for_unit_group(self, unit_group_id):
        """
        Get the unit ID of the "base" unit in the unit group specified by unit_group_id.
        Note: The "base" unit is uniquely defined by paticular Units of Measurement System (UoMSys)
              for each unit group. Collectively for all unit groups, base units are the set of units
              used "internally" by the application/model so that calculations are done consistently and
              correctly. For a relatively simple application/model, it may not be necessary to implement this
              method, because 
        :param unit_group_id: The ID of the unit group to get the base unit ID of, as Any
        :return: The base unit ID of the specified unit group, as [Any]
        """
        # Implement this method to return the appropriate unit ID based on the provided unit_group_id
        raise NotImplementedError
        return None
