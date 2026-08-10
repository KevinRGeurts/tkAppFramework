"""
This module defines the tkUnitSelectDlg class. It is a tkinter TopLevel window that enables the user to select a
particular unit from a unit group in a Units of Measurement System. The window grabs input and blocks until destoyed,
so it acts as a modal dialog.

Exported Classes:
    tkUnitSelectDlg -- A tkinter TopLevel window (dialog) that enables the user to select a
                       particular unit from a unit group in a Units of Measurement System.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter.simpledialog import _setup_dialog
from functools import partial

# Local imports
from tkAppFramework.uomsysadapter import UoMSysAdapter


# Reference: https://github.com/python/cpython/blob/3.14/Lib/tkinter/simpledialog.py
# Note that the dialog does not process events (at least not virtual ones, like a listbox selection), but the Okay
# and Cancel buttons do work.
class tkUnitSelectDlg(simpledialog.Dialog):
    """
    This class represents a tkinter TopLevel window that enables the user to select a particular unit from a unit group in a
    Units of Measurement System.
    The window grabs input and blocks until destoyed, so it acts as a modal dialog.
    """
    def __init__(self, parent, uom_adapter, quantity_name, unit_group_id, initial_unit_id, initial_unit_name, apply_callback=None):
        """
        :parameter parent: The parent tkinter window for the dialog
        :parameter uom_adapter: The Units of Measure System Adapter to be used by dialog, as UoMSysAdapter object
        :parameter quantity_name: The name of the physical quantity for which a unit is being selected, as string
            Note: Intended to provide context for the user to understand what they are changing, e.g., 'pipe length'
        :parameter unit_group_id: The ID of the unit group from which a unit is to be selected, as Any
        :parameter initial_unit_id: The ID of the unit that should be initially selected, as Any or None
        :parameter initial_unit_name: The name of the unit that should be initially selected, as string (could be '')
        :parameter apply_callback: A callable that will be used to "apply" the units selection, as callable
            Note: Should be: tkDGElementFieldHeader.set_units(unit_group_id, unit_id, unit_name)
        """
        assert(isinstance(quantity_name, str))
        assert(isinstance(initial_unit_name, str))
        assert(callable(apply_callback))
        if uom_adapter is not None:
            assert(isinstance(uom_adapter, UoMSysAdapter))
        self._uom = uom_adapter
        self._quantity_name = quantity_name
        self._group_id = unit_group_id
        self._init_unit_id = initial_unit_id
        self._init_unit_name = initial_unit_name
        self._selected_unit_id = self._init_unit_id
        self._selected_unit_name = self._init_unit_name
        self._apply_callback = apply_callback
        
        # Provide a title for the dialog, and call super classes' __init__
        dialog_title = 'Select units for ' + self._quantity_name
        simpledialog.Dialog.__init__(self, parent, dialog_title)

    def body(self, master):
        """
        Create dialog body.
        :parameter master: The parent tkinter window for the dialog
        :return: widget that should have initial focus
        This is an override of the base class method, and is called by the Dialog.__init__ method.
        """
        # Create a Listbox for selecting from a list of units
        self._units_item_data = []
        self._lb_units = tk.Listbox(master)
        self._lb_units.pack()
        # Fill the ListBox child widget with unit names from the unit group
        self._populate_unit_list()
        return self._lb_units

    def apply(self):
        """
        Process the input obtained from the dialog.
        This method is an override of the base class method and is called automatically to process the input, *after*
        the dialog is destroyed. It makes the unit change in the field header element.
        """
        current_selection = self._lb_units.curselection()[0]
        self._selected_unit_id = self._units_item_data[current_selection]
        self._selected_unit_name = self._lb_units.get(current_selection)
        self._apply_callback(self._selected_unit_id, self._selected_unit_name)

    def _populate_unit_list(self):
        """
        Fill the ListBox child widget with unit names from the unit group.
        :return: None
        """
        # Get the list of unit IDs for the unit group
        unit_ids = self._uom.get_unit_ids_of_unit_group(self._group_id)
        # Iterate the list of unit IDs and populate both the list of selections and the list of item data
        initial_unit_selection = -1
        i = 0
        for uid in unit_ids:
            unit_names = self._uom.get_unit_names_for_unit(uid)
            for un in unit_names:
                self._units_item_data.append(uid)
                self._lb_units.insert(tk.END, un)
                if un == self._init_unit_name:
                    initial_unit_selection = i
                i += 1
        self._lb_units.selection_set(initial_unit_selection)
        self.update_idletasks()
        return None
