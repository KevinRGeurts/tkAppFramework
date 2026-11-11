"""
Defines the abstract base class tkModalDialog, from which concrete tkinter modal dialogs can be derived.

Concrete implementation child classes must:
    (1) Implement the body(...) method to create the widgets of the dialog.
    (2) Implement the _get_dialog_output_dict(...) method to return a dictionary of output results for the dialog, which will be passed to the apply callback.
Concrete implementation child classes may:
    (3) Override the validate(...) method to add custom validation logic for the dialog data.
    (4) Override the buttonbox(...) method to create a different set of buttons for the dialog, if desired.
        The default buttonbox(...) method creates "OK", "Cancel", and "Help" buttons.

Exported Classes:
    tkModalDialog -- Interface (abstract base) class for tkinter modal dialogs.
                     tkModalDialog is a tkinter.simpledialog.Dialog.

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
from tkinter import simpledialog
from multiprocessing import Process

# local imports
from tkAppFramework.tkApp import tkHelpApp


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

# Reference: https://github.com/python/cpython/blob/3.14/Lib/tkinter/simpledialog.py
# Note that the tkModalDialog will not process virtual events, like a listbox selection). This appears to be a
# limitation of the tkinter simpledialog.Dialog class, which tkModalDialog inherits from.
class tkModalDialog(simpledialog.Dialog):
    """
    Abstract base class for modal dialogs built using tkinter.
    Concrete implementation child classes must:
        (1) Implement the body(...) method to create the widgets of the dialog.
        (2) Implement the _get_dialog_output_dict(...) method to return a dictionary of output results for the dialog, which will be passed to the apply callback.
    Concrete implementation child classes may:
        (3) Override the validate(...) method to add custom validation logic for the dialog data.
        (4) Override the buttonbox(...) method to create a different set of buttons for the dialog, if desired.
            The default buttonbox(...) method creates "OK", "Cancel", and "Help" buttons.
    """
    def __init__(self, parent, title = '', help_file = '', dlg_input={}, apply_callback=None, log_level = logging.INFO) -> None:
        """
        :parameter parent: The top-level tkinter widget, typicaly the return value from tkinter.Tk()
        :parameter title: The title of the dialog, to appear on the dialog window, string
        :parameter help_file: Path to the help file to be opened and displayed when Help button is clicked, string
        :param dlg_input: A dictionary of input parameters for the dialog, default is empty dictionary
        :parameter apply_callback: A callable that will be called to apply the dialog settings, as callable
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        assert(isinstance(title, str))
        self._title = title
        assert(isinstance(help_file, str))
        self._help_file = help_file
        assert(isinstance(dlg_input, dict))
        self._dlg_input = dlg_input
        assert(callable(apply_callback))
        self._apply_callback = apply_callback
        
        # Process running the HelpApp
        self._help_process = None

        # Set up logging for the dialog
        self._setup_logging(log_level)

        # Call super class' __init__ to create the dialog window and run the dialog
        super().__init__(parent, self._title)

    def destroy(self):
        '''
        Destroy the window.
        Kill the help app process if it is running, then call the base class destroy() method.
        '''
        if self._help_process is not None and self._help_process.is_alive():
            self._help_process.terminate()
            self._help_process.close()
        super().destroy()

    # Construction hooks

    def body(self, master):
        """
        Create dialog body.
        :parameter master: The parent tkinter window for the dialog
        :return: widget that should have initial focus
        This method should be overridden. It is called by the Dialog.__init__ method.
        """
        # Create a dummy Label widget, just as an illustration.
        self._lbl_dummy = ttk.Label(master, text="Actual widgets should be constructed, initialized, and packed here.")
        self._lbl_dummy.pack()
        
        return self._lbl_dummy  # initial focus

    def buttonbox(self):
        '''
        Add button box with "OK", "Cancel", "Help".
        Override if you do not want these buttons.
        '''

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Help", width=10, command=self.onHelpButton)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # Standard button semantics

    def onHelpButton(self):
        """
        Method called when dialog's Help button is clicked. Launch help app to view dialog's help.
        :return: None
        """
        if not self._help_process or not self._help_process.is_alive():
            # Help app is not running, so launch it
            
            # Get the help format by looking at the help file extension
            if self._help_file.endswith('md'):
                help_format='md'
            elif self._help_file.endswith('xhtml'):
                help_format='xhtml'
            else:
                help_format='txt'

            self._help_process = Process(target=_launch_help_app, name='HelpApp Process', kwargs={'help_file':self._help_file, 'help_format':help_format})
            self._help_process.start()
        return None

    # Command hooks

    def apply(self):
        """
        Process the input obtained from the dialog.
        This method is an override of the base class method and is called automatically to process the input by
        tkinter.simpledialog.Dialog.ok(...).
        """
        dlg_output = self._get_dialog_output_dict()
        self._apply_callback(dlg_output)

    def validate(self):
        '''
        Validate the data entered into the dialog.
        This method is called automatically to validate the data by tkinter.simpledialog.Dialog.ok(...).
        If this method returns 0, the dialog will not be destroyed.
        By default, it calls the base class validate() method, which always validates OK.
        Concrete implementation child classes may override this method to add custom validation logic for the dialog data.
        '''
        return super().validate()

    # Other methods

    def _get_dialog_output_dict(self):
        """
        This method is called by apply() to get the dialog output dictionary, which is then passed to the apply callback.
        This method should be overridden by concrete implementation child classes to return the dialog output dictionary.
        :return: dlg_output, a dictionary of output results for the dialog, default is empty dictionary.
        """
        dlg_output={}
        return dlg_output

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
