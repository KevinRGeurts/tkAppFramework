"""
This module defines the tkAppAboutDialog class. It is a tkinter TopLevel window that uses a tkXHTMLViewerWidget to display
formated application "about" information. The window grabs input and blocks until destoyed, so it acts as a modal dialog.

Exported Classes:
    tkXHTMLViewerWidget -- A tkinter TopLevel window (dialog) that uses a tkXHTMLViewerWidget to display
                           formated application "about" information.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk

# Local imports
from tkAppFramework.tkxhtmlviewerwidget import tkXHTMLViewerWidget

# TODO: Consider a method for the user to further customise "about" content. Add an "extra" field to AppAboutInfo that is
# a dictionary. Key: A string for the name of a tab in a notebook shown on the about dialog. Value: HTML formatted string to
# display in tkXHTMLViewerWidget, when the Key tab is selected. Examples would be to have "authors", "components", "licenses" tabs.
# By default, the "extra" field would contain an empty dictionary, and then no additional notebook tabs, beyond the default "About"
# would be created.

class tkAppAboutDialog(tk.Toplevel):
    """
    This class represents a tkinter TopLevel window that uses a tkXHTMLViewerWidget to display formated application "about" information.
    The window grabs input and blocks until destoyed, so it acts as a modal dialog.
    """
    def __init__(self, about_info):
        """
        :parameter about_info: The application "about" information to display, as AppAboutInfo object
        """
        self._about_info = about_info
        tk.Toplevel.__init__(self)
        # Provide a title for the dialog
        dialog_title = 'About ' + self._about_info.name
        self.title(dialog_title)
        # Create child widgets
        self._CreateWidgets()
        # Place application "about" information into the dialog's tkXHTMLViewerWidget
        self.processAppAboutInfo()
        # intercept close button
        self.protocol("WM_DELETE_WINDOW", self.onDestroyWindow)

    def show_dialog(self):
        """
        Actually show the dialog, which will block until window is destroyed.
        :return: None
        """
        self.wait_visibility() # can't grab until window appears, so we wait
        self.grab_set()        # ensure all input goes to our window
        self.focus_set()
        self.geometry('500x200') # set window size to width X height, in pixels
        self.wait_window()     # block until window is destroyed
        return None
        
    def _CreateWidgets(self):
        """
        Utility function called by __init__ to set up the child widgets of the dialog window.
        :return None:
        """
        _title = f"About {self._about_info.name}"
        self._abouttxt_widget = tkXHTMLViewerWidget(self, title=_title)
        self._abouttxt_widget.grid(column=0, row=0, sticky='NWES') # Grid-1
        self.columnconfigure(0, weight=1) # Grid-1
        self.rowconfigure(0, weight=1) # Grid-1
        return None

    def processAppAboutInfo(self):
        """
        Formats the application's "about" info into html and passes it to the tkXHTMLViewerWidget.
        :return: None
        """
        content = '<body>'
        content += f"<h3>{self._about_info.name}</h3>"
        content += f"<p>\nVersion {self._about_info.version}\n"
        content += f"Copyright (c) {self._about_info.copyright} by {self._about_info.author}\n"
        content += f"Licensed under the {self._about_info.license}\n"
        content += f"Source: <a href=\"{self._about_info.source}\">{self._about_info.source}</a></p>"
        content += '</body>'
        self._abouttxt_widget.processViewerContent(viewer_content=content, content_format='xhtml')
        return None

    def onDestroyWindow(self):
        """
        Method called when the window's close button is clicked.
        :return: None
        """
        self.grab_release()
        self.destroy()
        return None
