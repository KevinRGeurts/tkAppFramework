# standard imports
import tkinter as tk
from tkinter import ttk

from tkViewManager import tkViewManager

# local imports


class tkApp(ttk.Frame):
    """
    Abstract base class for application built using tkinter.
    Concrete implementation child class must:
        (1) Implement _setup_child_widgets()
    Concrete implementation child class likely will:
        (2) Extend __init__() to create and initialize any required business logic objects for menubar selections
        (3) Define and implement handler functions for menu bar, beyond OnExit 
    """
    def __init__(self, parent, title = '', menu_dict = {}) -> None:
        """
        :parameter title: The title of the application, to appear on the app's main window, string
        :parameter menu_dict: A dictionary describing the app's menubar:
            {menu text string : handler callable or another menu_dict if there is a cascade}
            If menu_dict is empty, then the menubar will only have File|Exit which will call OnExit.
        """
        super().__init__(parent)
        self.grid(column=0, row=0, sticky='NWES') # Grid-0
        # Weights control the relative "stretch" of each column and row as the frame is resized
        parent.columnconfigure(0, weight=1) # Grid-0
        parent.rowconfigure(0, weight=1) # Grid-0
        parent.option_add('*tearOff', False) # Prevent menus from tearing off
        parent.title(title)

        # Create and setup a menubar for the app
        if len(menu_dict)==0:
            # menu_dict is empty, so just set up File | Exit by default
            file_menu_dict={}
            file_menu_dict['Exit']=self.onFileExit
            menu_dict['File']=file_menu_dict
        self._setup_menubar(menu_dict)
        
        # Create and setup the child widgets of the app
        self._setup_child_widgets()

        # If the user X's the main window, make sure we clean up 
        parent.protocol("WM_DELETE_WINDOW", self.onFileExit)

    def _setup_menubar(self, menu_dict={}):
        """
        Utility function to be called by __init__ to set up the menu bar of the app.
        :parameter menu_dict: A dictionary describing the app's menubar:
            {menu text string : handler callable or another menu_dict if there is a cascade}
        :return: None
        """
        self._menubar = tk.Menu(self.master)
        self.master['menu'] = self._menubar
        self._setup_menu(menu_dict, self._menubar)
        return None

    def _setup_menu(self, menu_dict={}, add_to_menu=None):
        """
        Utility function to be called by _setup_menubar(...) to set up one cascade menu. Designed to be called
        recursively as needed.
        :parameter menu_dict: A dictionary describing a cascade menu:
            {menu text string : handler callable or another menu_dict if there is another cascade}
        :parameter add_to_menu: The cascade menu object to which the next cascade or action should be added
        :return: None
        """
        for menu_label in menu_dict:
            menu_action = menu_dict[menu_label]
            if type(menu_action) is dict:
                # Set up a cascade
                menu_obj=tk.Menu(add_to_menu)
                add_to_menu.add_cascade(menu=menu_obj, label=menu_label)
                self._setup_menu(menu_action, menu_obj)
            else:
                assert(callable(menu_action))
                add_to_menu.add_command(label=menu_label, command=menu_action)
        return None

    def _setup_child_widgets(self):
        """
        Abstract utility function to be called by __init__ to set up the child widgets of the app.
        Must be implemented by children. Will raise NotImplementedError if called.
        """
        raise NotImplementedError
        return None
        
    def onFileExit(self):
        """
        Method called when menu item File | Exit is selected.
        """
        self.master.destroy()
        return None
        
        



