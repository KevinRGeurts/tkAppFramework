"""
Defines the abstract base class tkViewManager. Concrete child implementations create widgets for tkApp concreate child implementations
and handle the interactions between widgets.

Class follows the mediator design pattern and acts as Observer. tkViewManager is a ttk.Frame.

Concrete implementation child classes must:
    (1) Implement the method _CreateWidgets(), which is called by __init__ to create and set up the child widgets
        of the tkViewManager widget.
    (2) Implement the handler function handle_model_update() to handle updates from the model.
    (3) Define and implement handler functions for widget updates, e.g., def handle_x_widget_update(self).
        Note:
            (a) Handler functions are registered with the tkViewManager via register_subject(...), typically
                after each widget is created in _CreateWidgets. 
            (b) Handler functions are automatically called from the update(...) method when a subject (child widget)
                notifies the tkViewManager by calling notify() on itself.

Exported Classes:
    tkViewManager -- Interface (abstract base) class for view managers of tkinter applications.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk

# Local imports
from tkAppFramework.ObserverPatternBase import Observer


class tkViewManager(Observer, ttk.Frame):
    """
    Defines the abstract base class tkViewManager. Concrete child implementations create widgets for tkApp concreate child implementations
    and handle the interactions between widgets.

    Class follows the mediator design pattern and acts as Observer. tkViewManager is a ttk.Frame.

    Concrete implementation child classes must:
        (1) Implement the method _CreateWidgets(), which is called by __init__ to create and set up the child widgets
            of the tkViewManager widget.
        (2) Implement the handler bunction handle_model_update() to handle updates from the model.
        (3) Define and implement handler functions for widget updates, e.g., def handle_x_widget_update(self):
            Note:
                (a) Handler functions are registered with the tkViewManager via register_subject(...), typically
                    after each widget is created in _CreateWidgets. 
                (b) Handler functions are automatically called from the update(...) method when a subject (child widget)
                    notifies the tkViewManager by calling notify() on itself.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, the tkinter App, which hereafter will be
                           accessed as self.master.
        """
        Observer.__init__(self)
        ttk.Frame.__init__(self, parent)

        # Register the (data and business logic) model as a subject
        self.register_subject(subject=self.getModel(), update_handler=self.handle_model_update)

        self._CreateWidgets()

        self.bind('<Destroy>', self.onDestroy, '+')
        
    def onDestroy(self, event):
        """
        Method called after ttk.Frame is destroyed.
        :return: None
        """
        # Detach this observer from it's subjects, the child widgets of the mediator / view manager
        self._detach_from_subjects()
        return None

    def _CreateWidgets(self):
        """
        Abstract utility function to be called by __init__ to set up the child widgets of the tkViewManager widget.
        register_subject(...) should be called for each child widget that is a Subject, to register the widget
        and a handler function for updates from that widget.
        Must be implemented by children. Will raise NotImplementedError if called.
        :return None:
        """
        raise NotImplementedError
        return None

    def handle_model_update(self):
        """
        Handler function called when the model notifies the tkViewManager of a change in state.
        Must be implemented by children. Will raise NotImplementedError if called.
        :return None:
        """
        raise NotImplementedError
        return None

    def getModel(self):
        """
        Accessor method to return the model of the app.
        :return: The model of the app, instance of Model
        """
        return self.master.getModel()
