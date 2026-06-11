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
        '''create dialog body.

        return widget that should have initial focus.
        This method should be overridden, and is called
        by the Dialog.__init__ method.
        '''
        # Create a Listbox for selecting from a list of units
        self._units_item_data = []
        self._lb_units = tk.Listbox(master)
        self._lb_units.pack()
        # Fill the ListBox child widget with unit names from the unit group
        self._populate_unit_list()
        return self._lb_units

    def apply(self):
        '''process the data

        This method is called automatically to process the data, *after*
        the dialog is destroyed. It makes the unit change in the field header element.
        '''
        current_selection = self._lb_units.curselection()[0]
        self._selected_unit_id = self._units_item_data[current_selection]
        self._selected_unit_name = self._lb_units.get(current_selection)
        self._apply_callback(self._group_id, self._selected_unit_id, self._selected_unit_name)

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


# Reference: https://github.com/python/cpython/blob/3.14/Lib/tkinter/filedialog.py
# Here again, despite following the methodology of the reference, events don't seem to get processed within the
# dialog.
class tkUnitSelectDlg3:
    """
    This class represents a tkinter TopLevel window that enables the user to select a particular unit from a unit group in a
    Units of Measurement System.
    The window grabs input and blocks until destoyed, so it acts as a modal dialog.
    """
    def __init__(self, parent, uom_adapter, quantity_name, unit_group_id, initial_unit_id, initial_unit_name):
        """
        :parameter parent: The parent tkinter window for the dialog
        :parameter uom_adapter: The Units of Measure System Adapter to be used by dialog, as UoMSysAdapter object
        :parameter quantity_name: The name of the physical quantity for which a unit is being selected, as string
            Note: Intended to provide context for the user to understand what they are changing, e.g., 'pipe length'
        :parameter unit_group_id: The ID of the unit group from which a unit is to be selected, as Any
        :parameter initial_unit_id: The ID of the unit that should be initially selected, as Any or None
        :parameter initial_unit_name: The name of the unit that should be initially selected, as string (could be '')
        """
        assert(isinstance(quantity_name, str))
        assert(isinstance(initial_unit_name, str))
        self._parent = parent
        
        # Create a top level window for the dialog
        self._top = tk.Toplevel(self._parent)
        
        if uom_adapter is not None:
            assert(isinstance(uom_adapter, UoMSysAdapter))
        self._uom = uom_adapter
        self._quantity_name = quantity_name
        self._group_id = unit_group_id
        self._init_unit_id = initial_unit_id
        self._init_unit_name = initial_unit_name
        self._selected_unit_id = self._init_unit_id
        self._selected_unit_name = self._init_unit_name
        
        # Provide a title for the dialog, and call super classes' __init__
        self._title = 'Select units for ' + self._quantity_name
        self._top.title(self._title)
        self._top.iconname(self._title)

        # "Style the dialog based on the OS
        _setup_dialog(self._top)

        # Create the dialog's widgets
        self._CreateWidgets()

    def _CreateWidgets(self):
        """
        Utility function called by __init__ to set up the child widgets of the dialog window.
        :return None:
        """
        # Create a Listbox and associated control variable for selecting from a list of units
        self._cv_units = tk.StringVar()
        self._units_item_data = []
        self._lb_units = tk.Listbox(self._top, listvariable=self._cv_units)
        self._lb_units.grid(column=0, columnspan=2, row=0, sticky='NWES') # Grid-1
        self._top.columnconfigure(0, weight=1) # Grid-1
        self._top.rowconfigure(0, weight=1) # Grid-1
        self._lb_units.bind('<<ListBoxSelect>>', partial(self.onUnitsListBoxSelect, self._lb_units.curselection()), '+')
        self._populate_unit_list()

        # Create Okay button
        self._btn_ok = ttk.Button(self._top, text='Okay', command=self.onOkButtonClicked)
        self._btn_ok.grid(column=0, row=1) # Grid-1
        self._top.columnconfigure(0, weight=1) # Grid-1
        self._top.rowconfigure(1, weight=1) # Grid-1
        # So that return key is same as clicking Okay button
        self._top.bind('<Return>', lambda e: self._btn_ok.invoke())

        # Create Cancel button
        self._btn_cancel = ttk.Button(self._top, text='Cancel', command=self.onCancelButtonClicked)
        self._btn_cancel.grid(column=1, row=1) # Grid-1
        self._top.columnconfigure(1, weight=1) # Grid-1
        self._top.rowconfigure(1, weight=1) # Grid-1

        self._top.protocol('WM_DELETE_WINDOW', self.onCancelButtonClicked)

        return None

    def _populate_unit_list(self):
        """
        Fill the ListBox child widget with unit names from the unit group.
        :return: None
        """
        # Get the list of unit IDs for the unit group
        unit_ids = self._uom.get_unit_ids_of_unit_group(self._group_id)
        # Iterate the list of unit IDs and populate both the list of selections and the list of item data
        initial_unit_selection = -1
        for uid in unit_ids:
            unit_names = self._uom.get_unit_names_for_unit(uid)
            i = 0
            for un in unit_names:
                self._units_item_data.append(uid)
                self._lb_units.insert(tk.END, un)
                if un == self._init_unit_name:
                    initial_unit_selection = i
                i += 1
        self._lb_units.selection_set(initial_unit_selection)
        return None

    def show_dialog(self):
        """
        Actually show the dialog, which will block until window is destroyed.
        :return: tuple (ID of unit group,
                        ID of selected unit if Okayed or ID of initial unit if Canceled,
                        name of selected unit if Okayed or name of initial unit if Canceled),
                        as (Any, Any, string)
        """
        # TODO: Possible .focus_set() on the Listbox child widget
        self._top.wait_visibility() # can't grab until window appears, so we wait
        self._top.grab_set()        # ensure all input goes to our window
        # self._top.geometry('500x200') # set window size to width X height, in pixels
        self._parent.mainloop() # Exited by self._parent.quit() in onOkButtonClicked() or onCancelButtonClicked()
        self._top.destroy()
        return (self._group_id, self._selected_unit_id, self._selected_unit_name)

    def onUnitsListBoxSelect(self, current_selection):
        """
        Handler for making a selection in the units list box.
        :parameter current_selection: The index into the control variable of the selected item in the units listbox, as int
        :return: None
        """
        self._selected_unit_id = self._units_item_data[current_selection]
        self._selected_unit_name = self._cv_units[current_selection]
        return None

    def onOkButtonClicked(self, event):
        """
        Handler for clicking the Okay button.
        """
        self._parent.quit() # Exit mainloop()
        return None

    def onCancelButtonClicked(self, event):
        """
        Handler for clicking the Cancel button.
        """
        self._selected_unit_id = self._init_unit_id
        self._selected_unit_name = self._init_unit_name
        self._parent.quit() # Exit mainloop()
        return None


# Events don't seem to get processed within the dialog. Probably not surprising, as there is no event loop running for it.
class tkUnitSelectDlg2(tk.Toplevel):
    """
    This class represents a tkinter TopLevel window that enables the user to select a particular unit from a unit group in a
    Units of Measurement System.
    The window grabs input and blocks until destoyed, so it acts as a modal dialog.
    """
    def __init__(self, uom_adapter, quantity_name, unit_group_id, initial_unit_id, initial_unit_name):
        """
        :parameter uom_adapter: The Units of Measure System Adapter to be used by dialog, as UoMSysAdapter object
        :parameter quantity_name: The name of the physical quantity for which a unit is being selected, as string
            Note: Intended to provide context for the user to understand what they are changing, e.g., 'pipe length'
        :parameter unit_group_id: The ID of the unit group from which a unit is to be selected, as Any
        :parameter initial_unit_id: The ID of the unit that should be initially selected, as Any or None
        :parameter initial_unit_name: The name of the unit that should be initially selected, as string (could be '')
        """
        assert(isinstance(quantity_name, str))
        tk.Toplevel.__init__(self)

        if uom_adapter is not None:
            assert(isinstance(uom_adapter, UoMSysAdapter))
        self._uom = uom_adapter

        self._quantity_name = quantity_name
        # Provide a title for the dialog
        dialog_title = 'Select units for ' + self._quantity_name
        self.title(dialog_title)
        
        self._group_id = unit_group_id
        self._init_unit_id = initial_unit_id
        self._init_unit_name = initial_unit_name
        self._selected_unit_id = self._init_unit_id
        self._selected_unit_name = self._init_unit_name
        
        # Create child widgets
        self._CreateWidgets()
        # Fill the ListBox child widget with unit names from the unit group
        self.populate_unit_list()
        # intercept close button
        self.protocol("WM_DELETE_WINDOW", self.onDestroyWindow)

    def show_dialog(self):
        """
        Actually show the dialog, which will block until window is destroyed.
        :return: tuple (ID of selected unit if Okayed or ID of initial unit if Canceled,
                        name of selected unit if Okayed or name of initial unit if Canceled),
                       as (Any, string)
        """
        self.wait_visibility() # can't grab until window appears, so we wait
        self.grab_set()        # ensure all input goes to our window
        self.focus_set()
        self.geometry('500x200') # set window size to width X height, in pixels
        self.mainloop()
        # self.wait_window()
        return (self._selected_unit_id, self._selected_unit_name)
        
    def _CreateWidgets(self):
        """
        Utility function called by __init__ to set up the child widgets of the dialog window.
        :return None:
        """
        # Create a Listbox and associated control variable for selecting from a list of units
        self._cv_units = tk.StringVar()
        self._units_item_data = []
        self._lb_units = tk.Listbox(self, listvariable=self._cv_units)
        self._lb_units.grid(column=0, columnspan=2, row=0, sticky='NWES') # Grid-1
        self.columnconfigure(0, weight=1) # Grid-1
        self.rowconfigure(0, weight=1) # Grid-1
        self._lb_units.bind('<<ListBoxSelect>>', lambda e: self.onUnitsListBoxSelect(self._lb_units.curselection()))

        # Create Okay button
        self._btn_ok = ttk.Button(self, text='Okay', command=self.onOkButtonClicked)
        self._btn_ok.grid(column=0, row=1) # Grid-1
        self.columnconfigure(0, weight=1) # Grid-1
        self.rowconfigure(1, weight=1) # Grid-1
        # So that return key is same as clicking Okay button
        self.bind('<Return>', lambda e: self._btn_ok.invoke())

        # Create Cancel button
        self._btn_cancel = ttk.Button(self, text='Cancel', command=self.onCancelButtonClicked)
        self._btn_cancel.grid(column=1, row=1) # Grid-1
        self.columnconfigure(1, weight=1) # Grid-1
        self.rowconfigure(1, weight=1) # Grid-1

        return None

    def onUnitsListBoxSelect(self, current_selection):
        """
        Handler for making a selection in the units list box.
        :parameter current_selection: The index into the control variable of the selected item in the units listbox, as int
        :return: None
        """
        self._selected_unit_id = self._units_item_data[current_selection]
        self._selected_unit_name = self._cv_units[current_selection]
        return None

    def onOkButtonClicked(self, event):
        """
        Handler for clicking the Okay button.
        """
        self.onDestroyWindow()
        return None

    def onCancelButtonClicked(self, event):
        """
        Handler for clicking the Cancel button.
        """
        self._selected_unit_id = self._init_unit_id
        self._selected_unit_name = self._init_unit_name
        self.onDestroyWindow()
        return None    

    def populate_unit_list(self):
        """
        Fill the ListBox child widget with unit names from the unit group.
        :return: None
        """
        # Get the list of unit IDs for the unit group
        unit_ids = self._uom.get_unit_ids_of_unit_group(self._group_id)
        # Iterate the list of unit IDs and populate both the list of selections and the list of item data
        selection_list = ''
        for uid in unit_ids:
            unit_names = self._uom.get_unit_names_for_unit(uid)
            for un in unit_names:
                self._units_item_data.append(uid)
                selection_list += un + ' '
        self._cv_units.set(selection_list)
        return None

    def onDestroyWindow(self):
        """
        Method called when the window's close button is clicked.
        :return: None
        """
        self.grab_release()
        self.destroy()
        return None
