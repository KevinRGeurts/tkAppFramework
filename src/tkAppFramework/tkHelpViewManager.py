"""
This module defines the tkHelpViewManager class. It is a concrete implementation of tkViewManager.
It acts as a Mediator and an Observer, and handles the interactions between the help viewer application's widgets.

Exported Classes:
    tkHelplViewManager -- Concrete implementation of tkViewManager.
                          Acts as a Mediator and an Observer, and handles the interactions between
                          the help viewer application's widgets.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports


# Local imports
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.tkxhtmlviewerwidget import tkXHTMLViewerWidget


class tkHelpViewManager(tkViewManager):
    """
    Concrete implementation of tkViewManager. Acts as Observer, and handles the interactions between help viewer application's widgets.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, most probably a Toplevel window
        """
        tkViewManager.__init__(self, parent)
        
    def _CreateWidgets(self):
        """
        Concrete implementation of tkViewManager._CreateWidgets.
        Sets up and registers the child widgets of the tkHelpViewManager widget.
        :return None:
        """

        self._helptxt_widget = tkXHTMLViewerWidget(self)
        self.register_subject(self._helptxt_widget, self.handle_helptxt_widget_update)
        self._helptxt_widget.attach(self)
        self._helptxt_widget.grid(column=0, row=0, sticky='NWES') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        return None

    def handle_helptxt_widget_update(self):
        """
        Handle updates from help text widget.
        :return None:
        """
        # Do something as needed.
        return None

    def handle_model_update(self):
        """
        Handler function called when the model notifies the view manager of a change in state.
        :return None:
        """
        (help_content, help_format) = self.getModel().get_help_content()
        self._helptxt_widget.processViewerContent(help_content, help_format)
        return None
