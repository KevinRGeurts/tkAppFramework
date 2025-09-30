"""
Defines the abstract base class tkApp, from which concrete tkinter applications can be derived.

Concrete implementation child classes must:
    (1) Implement the factory method _createViewManager() to create and return a tkViewManager instance,
        which will create and manage the widgets of the application.
    (2) Implement _createModel() factory method to create and return a Model instance.
Concrete implementation child classes likely will:
    (3) Pass AboutAppInfo named tuple into super.__init__() to set up the app's About dialog.
    (4) Pass menu_dict into super.__init__() to set up the app's menubar.
    (5) Pass file_types into super.__init__() to set up the file types for file dialogs.
    (6) Define and implement handler functions for menubar selections, beyond OnFileOpen, OnFileSave,
        OnFileSaveAs, OnFileExit, and OnHelpAbout.
Concreate implementation child classes may:
    (7) Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets

Exported Classes:
    tkApp -- Interface (abstract base) class for tkinter applications. tkApp is a ttk.Frame.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# standard imports
from collections import namedtuple
import os
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog

# local imports


# Named tuple to hold the "About" information of the app.
AppAboutInfo = namedtuple('AppAboutInfo', ['name', 'version', 'copyright', 'author', 'license', 'source'],
                          defaults = {'name':'my app', 'version':'X.X', 'copyright':'20XX', 'author':'John Q. Public', 'license':'MIT License', 'source':'github url'})


# TODO: Refctor the way the menubar is created, so that File|Exit and Help|About are always present. If the
# user provides a non-empty menu_dict, and it contains File|Exit or Help|About, then use the user's handler.
# If the user provides an empty menu_dict, or a non-empty menu_dict that does not contain File|Exit or Help|About,
# then add those items with the default handlers.
class tkApp(ttk.Frame):
    """
    Abstract base class for applications built using tkinter.
    Concrete implementation child classes must:
        (1) Implement the factory method _createViewManager() to create and return a tkViewManager instance,
            which will create and manage the widgets of the application.
        (2) Implement _createModel() factory method to create and return a Model instance.
    Concrete implementation child classes likely will:
        (3) Pass AboutAppInfo named tuple into super.__init__() to set up the app's About dialog.
        (4) Pass menu_dict into super.__init__() to set up the app's menubar.
        (5) Pass file_types into super.__init__() to set up the file types for file dialogs.
        (6) Define and implement handler functions for menubar selections, beyond OnFileOpen, OnFileSave,
            OnFileSaveAs, OnFileExit, and OnHelpAbout.
    Concreate implementation child classes may:
        (7) Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets
    """
    def __init__(self, parent, title = '', menu_dict = {}, app_info = AppAboutInfo(), file_types=[]) -> None:
        """
        :parameter title: The title of the application, to appear on the app's main window, string
        :parameter menu_dict: A dictionary describing the app's menubar:
            {menu text string : handler callable or another menu_dict if there is a cascade}
            If menu_dict is empty, then the menubar will only have File|Exit which will call OnFileExit,
                and Help|About... which will call OnHelpAbout.
            If menu_dict is not empty, then File|Exit and Help|About items will not be added automatically.
        :parameter app_info: An AppAboutInfo named tuple with the app's "About" information:
            (name, version, copyright, author, license, source), all fields provided as strings
            Example:
            ('my app', 'X.X', '20XX', 'John Q. Public', 'MIT License', 'github url')
        :parameter file_types: A list of file types for saving and opening, of this format:
            [('Description1', '*.ext1'), ('Description2', '*.ext2'), ...]
        """
        super().__init__(parent)

        self._appInfo = app_info
        self._fileTypes = list(file_types) # List of file extensions for file dialogs
        self._savePath = '' # Path of last save, empty string if never saved

        self.grid(column=0, row=0, sticky='NWES') # Grid-0
        # Weights control the relative "stretch" of each column and row as the frame is resized
        parent.columnconfigure(0, weight=1) # Grid-0
        parent.rowconfigure(0, weight=1) # Grid-0
        parent.option_add('*tearOff', False) # Prevent menus from tearing off
        parent.title(title)

        # Create and setup a menubar for the app
        if len(menu_dict)==0:
            # menu_dict is empty, so just set up File | Exit and Help | About by default
            file_menu_dict={}
            file_menu_dict['Open...']=self.onFileOpen
            file_menu_dict['Save']=self.onFileSave
            file_menu_dict['Save As...']=self.onFileSaveAs
            file_menu_dict['Exit']=self.onFileExit
            help_menu_dict={}
            help_menu_dict['About...']=self.onHelpAbout
            menu_dict['File']=file_menu_dict
            menu_dict['Help']=help_menu_dict
        self._setup_menubar(menu_dict)

        # Create and initialize the model of the app
        self._model = self._createModel()
        
        # Create and setup the child widgets of the app, including the view manager self._view_manager
        self._setup_child_widgets()

        # Attach view manager as observer of model
        self._model.attach(self._view_manager) 

        # If the user X's the main window, make sure we clean up 
        parent.protocol("WM_DELETE_WINDOW", self.onFileExit)

    def getModel(self):
        """
        Accessor method to return the model of the app.
        :return: The model of the app, instance of Model
        """
        return self._model
        
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
        Utility function to be called by __init__ to set up the child widgets of the app.
        This function calls the factory method _createViewManager() to create a tkViewManager instance for the app.
        It is expected that the tkViewManager will create all other widgets of the app. If this is not the case
        then this method should be extended by the child class.
        :return: None
        """
        self._view_manager = self._createViewManager()
        self._view_manager.grid(column=0, row=0, sticky='NWES') # Grid-1
        self.columnconfigure(0, weight=1) # Grid-1
        self.rowconfigure(0, weight=1) # Grid-1
        return None

    def _createViewManager(self):
        """
        This is an abstract factory method called to create and return a tkViewManager instance.
        Must be implemented by children to create a child of tkViewManager.
        Will raise NotImplementedError if called.
        :return: An instance of a concrete implementation child class of tkViewManager
        """
        raise NotImplementedError
        return None

    def _createModel(self):
        """
        This is an abstract factory method called to create and return a Model instance.
        Must be implemented by children to create a child of Model
        Will raise NotImplementedError if called.
        :return: An instance of a concrete implementation child class of Model
        """
        raise NotImplementedError
        return None

    def getAboutInfo(self):
        """
        Method to be called to get the "About" information of the app.
        :return: AppAboutInfo named tuple with the app's "About" information:
            (name, version, copyright, author, license, source), all fields returned as strings
            Example:
            ('my app', 'X.X', '20XX', 'John Q. Public', 'MIT License', 'github url')
        """
        return self._appInfo
    
    def onFileOpen(self):
        """
        Respond to a File|Open menu selection by using the tkFileDialog for open to get the path,
        then opening that path for read, and calling the model's readModelFromFile(...) method.
        """
        initial_dir = None
        if len(self._savePath)>0:
            initial_dir = os.path.dirname(self._savePath)
        else:
            initial_dir = os.getcwd()
        # Pop up tkFileDialog for open
        response = filedialog.askopenfilename(defaultextension=self._fileTypes[0][1], filetypes=self._fileTypes,
                                              initialdir=initial_dir, title='Select file to open')
        if len(response)>0: # User did not cancel
            with open(response) as f:
                self._model.readModelFromFile(f, os.path.splitext(response)[1])
                self._savePath = response

    def onFileSave(self):
        """
        Respond to a File|Save menu selection by opening self._savePath for write, and
        calling the model's writeModelToFile(...) method.
        """
        if len(self._savePath)==0:
            with open(self._savePath, mode='w') as f:
                self._model.writeModelToFile(f, os.path.splitext(self._savePath)[1])

    def onFileSaveAs(self):
        """
        Respond to a File|Save As menu selection by using the tkFileDialog for save to get the path,
        then opening that path for write, and calling the model's writeModelToFile(...) method.
        """
        initial_dir = None
        if len(self._savePath)>0:
            initial_dir = os.path.dirname(self._savePath)
        else:
            initial_dir = os.getcwd()
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(defaultextension=self._fileTypes[0][1], filetypes=self._fileTypes,
                                                initialdir=initial_dir, title='Select file to save as')
        if len(response)>0: # User did not cancel
            with open(response, mode='w') as f:
                self._model.writeModelToFile(f, os.path.splitext(response)[1])
                self._savePath = response


    def onFileExit(self):
        """
        Method called when menu item File | Exit is selected.
        :return: None
        """
        self.master.destroy()
        return None

    # TODO: Investigate if instead of showinfo(...) we can create a pop-up dialog that contains a
    # tkinter.Text widget, so that the app's "About" information can be "rich" formatted text.
    # This would allow clickable hyperlink for source, bold, italic, etc. Requires investigation of 
    # ability to auto tag text in the widget.
    def onHelpAbout(self):
        """
        Method called when menu item Help | About is selected.
        :return: None
        """
        msg = self._appInfo.name + '\n'
        msg += 'version ' + self._appInfo.version + '\n'
        msg += 'Copyright (c) ' + self._appInfo.copyright + ' by ' + self._appInfo.author + '\n'
        msg += 'Licensed under the ' + self._appInfo.license + '\n'
        msg += 'Source: ' + self._appInfo.source
        dialog_title = 'About ' + self._appInfo.name
        showinfo(title=dialog_title, message=msg, parent=self.master)
        return None



        



