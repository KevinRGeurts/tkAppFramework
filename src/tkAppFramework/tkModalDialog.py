"""
Defines the abstract base class tkModalDialog, from which concrete tkinter modal dialogs can be derived.

Concrete implementation child classes must:
    (1) Implement the factory method _createViewManager() to create and return a tkViewManager instance,
        which will create and manage the widgets of the application.
Concrete implementation child classes likely will:
    (3) Pass AboutAppInfo named tuple into super.__init__() to set up the app's About dialog.
    (4) Pass menu_dict into super.__init__() to set up the app's menubar.
    (5) Pass file_types into super.__init__() to set up the file types for file dialogs.
    (6) Define and implement handler functions for menubar selections, beyond OnFileOpen, OnFileSave,
        OnFileSaveAs, OnFileExit, OnViewHelp, and OnHelpAbout.
Concrete implementation child classes may:
    (7) Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets
    (8) Extend logging setup in _setup_logging(...) if application specific logging is desired.

Exported Classes:
    tkModalDialog -- Interface (abstract base) class for tkinter modal dialogs. tkModalDialog is a ttk.Frame.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    A logger named 'tkModalDialog_logger' is created and configured in _setup_logging(...), which is called by __init__(...).
    It logs to stderr through a stream handler. Default logging level is logging.INFO, but can be set by passing
    log_level into __init__(...). The 'tkModalDialog_logger' logger can be used by concrete implementation child classes of tkModalDialog.
"""


# standard imports
import logging
import tkinter as tk
from tkinter import ttk
from multiprocessing import Process

# local imports
from tkAppFramework.tkApp import tkHelpApp


# This function cannot be a method of tkModalDialog, due to Process using pickle.
def launch_modal_dialog(title = '', help_file = '', help_format='', dlg_input={}, log_level = logging.INFO):
    """
    Launch tkinter modal dialog for collecting choices/information from user.
    :parameter title: The title of the dialog, to appear on the dialog window, string
    :parameter help_file: Path to the help file to be opened and displayed when Help button is clicked, string
    :parameter help_format: Format of content in help file (must be 'txt', 'xhtml', or 'md'), string
    :param dlg_input: A dictionary of input parameters for the dialog, default is empty dictionary
    :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
    :return: None
    """
    dlg_process = Process(target=_launch_modal_dialog_helper, name='Modal Dialog Process',
                          kwargs={'title':title, 'help_file':help_file, 'help_format':help_format,
                                  'dlg_input':dlg_input, 'log_level':log_level})
    dlg_process.start()
    dlg_process.join() # Wait for the dialog process to finish before returning
    return None


def _launch_modal_dialog_helper(title = '', help_file = '', help_format='', dlg_input={}, log_level = logging.INFO):
    """
    Launch helper function for tkinter modal dialog.
    :parameter title: The title of the dialog, to appear on the dialog window, string
    :parameter help_file: Path to the help file to be opened and displayed when Help button is clicked, string
    :parameter help_format: Format of content in help file (must be 'txt', 'xhtml', or 'md'), string
    :param dlg_input: A dictionary of input parameters for the dialog, default is empty dictionary
    :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
    :return: None
    """
    assert(isinstance(title, str))
    assert(isinstance(help_file, str))
    assert(isinstance(help_format, str))
    assert(help_format in ['txt', 'xhtml', 'md'])
    assert(isinstance(dlg_input, dict))

    # Create and configure the modal dialog
    root = tk.Tk()
    dlg = tkModalDialog(root, title, help_file, help_format, dlg_input, log_level)
    dlg.wait_visibility()
    dlg.grab_set_global()

    # Start the dialog's event loop running
    dlg.mainloop()

    dlg.grab_release() # Release the grab before destroying the dialog
    dlg.destroy() # Destroy the dialog after the event loop ends

    return None


# This function cannot be a method of tkModalDialog, due to Process using pickle.
def _launch_help_app(help_file = '', help_format = 'txt'):
    """
    Launch tkinter app for displaying online help.
    :parameter help_file: Path to the help file to be opened and displayed initially, string
    :parameter help_format: Format of content in help file (must be 'txt', 'xhtml', or 'md'), string
    :return: The launched tkHelpApp object, as tkHelpApp object
    """
    assert(type(help_file)==str)
    assert(type(help_format)==str)
    assert(help_format in ['txt', 'xhtml', 'md'])

    # Create and configure the app
    root = tk.Tk()
    myapp = tkHelpApp(root, help_file, help_format)

    # Start the app's event loop running
    myapp.mainloop()
    return myapp


class tkModalDialog(ttk.Frame):
    """
    Abstract base class for modal dialogs built using tkinter.
    Concrete implementation child classes must:
        (1) Implement the factory method _createViewManager() to create and return a tkViewManager instance,
            which will create and manage the widgets of the application.
    Concrete implementation child classes likely will:
        (3) Pass AboutAppInfo named tuple into super.__init__() to set up the app's About dialog.
        (4) Pass menu_dict into super.__init__() to set up the app's menubar.
        (5) Pass file_types into super.__init__() to set up the file types for file dialogs.
        (6) Define and implement handler functions for menubar selections, beyond OnFileOpen, OnFileSave,
            OnFileSaveAs, OnFileExit, and OnHelpAbout.
    Concrete implementation child classes may:
        (7) Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets
    """
    def __init__(self, parent, title = '', help_file = '', help_format='', dlg_input={}, log_level = logging.INFO) -> None:
        """
        :parameter parent: The top-level tkinter widget, typicaly the return value from tkinter.Tk()
        :parameter title: The title of the dialog, to appear on the dialog window, string
        :parameter help_file: Path to the help file to be opened and displayed when Help button is clicked, string
        :parameter help_format: Format of content in help file (must be 'txt', 'xhtml', or 'md'), string
        :param dlg_input: A dictionary of input parameters for the dialog, default is empty dictionary
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        super().__init__(parent)

        assert(isinstance(title, str))
        assert(isinstance(help_file, str))
        self._help_file = help_file
        assert(isinstance(help_format, str))
        assert(help_format in ['txt', 'xhtml', 'md'])
        self._help_format = help_format

        self.grid(column=0, row=0, sticky='NWES') # Grid-0
        # Weights control the relative "stretch" of each column and row as the frame is resized
        parent.columnconfigure(0, weight=1) # Grid-0
        parent.rowconfigure(0, weight=1) # Grid-0
        parent.option_add('*tearOff', False) # Prevent menus from tearing off
        parent.title(title)

        # Create and initialize the model of the app
        assert(isinstance(dlg_input, dict))
        self._input = dlg_input
        
        # Create and setup the child widgets of the dialog, including the view manager self._view_manager
        self._setup_child_widgets()
        
        # Process running the HelpApp
        self._help_process = None

        # If the user X's the dialog window, make sure we clean up 
        parent.protocol("WM_DELETE_WINDOW", self.onFileExit)

        # Set up logging for this app
        self._setup_logging(log_level)

    def _setup_child_widgets(self):
        """
        Utility function to be called by __init__ to set up the child widgets of the dialog.
        This function calls the factory method _createViewManager() to create a tkViewManager instance for the dialog.
        It is expected that the tkViewManager will create all other widgets of the dialog. If this is not the case
        then this method should be extended by the child class.
        :return: None
        """
        # self._view_manager = self._createViewManager()
        # self._view_manager.grid(column=0, row=0, columnspan=3, sticky='NWES') # Grid-1
        # self.columnconfigure(0, weight=1) # Grid-1
        # self.rowconfigure(0, weight=1) # Grid-1

        # Set up the standard buttons for the dialog, which are OK, Cancel, and Help.self
        self._btn_OK = ttk.Button(self, text='OK', command=self.onFileExit)
        self._btn_OK.grid(column=0, row=1, sticky='S')
        self._btn_Cancel = ttk.Button(self, text='Cancel', command=self.onFileExit)
        self._btn_Cancel.grid(column=1, row=1, sticky='S')
        self._btn_Help = ttk.Button(self, text='Help', command=self.onViewHelp)
        self._btn_Help.grid(column=2, row=1, sticky='S')
        
        return None

    def _createViewManager(self):
        """
        This is an abstract factory method called to create and return a tkViewManager instance.
        Must be implemented by children to create a child of tkViewManager.
        Will raise NotImplementedError if called.
        :return: An instance of a concrete implementation child class of tkViewManager
        """
        # raise NotImplementedError
        return None

    def onFileExit(self):
        """
        Method called when menu item File | Exit is selected.
        :return: None
        """
        # Get the logger 'tkApp_logger'
        logger = logging.getLogger('tkModalDialog_logger')

        if self._help_process:
            logger.debug(f"Help Process {self._help_process.name} is alive={self._help_process.is_alive()}")

        self.master.destroy()
        return None

    def onViewHelp(self):
        """
        Method called when menu item Help | View Help is selected. Launch help app to view help.
        :return: None
        """
        if not self._help_process or not self._help_process.is_alive():
            # Help app is not running, so launch it
            
            # Get the help format by looking at the help file extension
            if self._appInfo.help_file.endswith('md'):
                help_format='md'
            elif self._appInfo.help_file.endswith('xhtml'):
                help_format='xhtml'
            else:
                help_format='txt'

            self._help_process = Process(target=_launch_help_app, name='HelpApp Process', kwargs={'help_file':self._appInfo.help_file, 'help_format':help_format})
            self._help_process.start()
        return None

    def _setup_logging(self, log_level=logging.INFO):
        """
        This method configures logging.
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        :return: None
        """
        # Create a logger with name 'tkModalDialog_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('tkModalDialog_logger')
        # This is the threshold level for the logger itself, before it will pass to any handlers, which can have their own threshold.
        # Should be able to control here what the stream handler receives and thus what ends up going to stderr.
        # Use this key for now:
        #   DEBUG = debug messages sent to this logger will end up on stderr
        #   INFO = info messages sent to this logger will end up on stderr
        logger.setLevel(log_level)
        # Set up this highest level below root logger with a stream handler
        sh = logging.StreamHandler()
        # Set the threshold for the stream handler itself, which will come into play only after the logger threshold is met.
        sh.setLevel(log_level)
        # Add the stream handler to the logger
        logger.addHandler(sh)
            
        return None
