# Standard imports
import tkinter as tk
from tkinter import ttk

# Local imports
from ObserverPatternBase import Observer, Subject


class tkViewManager(ttk.Frame, Observer):
    """
    Class follows mediator design pattern. Acts as Observer, and is a base class for classes that handle the interactions
    between a tkinter app's widgets.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, The tkinter App
        """
        ttk.Frame.__init__(self, parent)
        Observer.__init__(self)

        # Maintain a dictionary of Key=subject (child widget), Value=update handler callable
        self._subjects = {}

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
        
    def register_subject(self, subject = None, update_handler = None):
        """
        Register a subject (child widget) and the callable to handle subject updates.
        :parameter subject: The child widget subject, an object of type Subject and type ti.Widget
        :parameter update_handler: The callable function to handle updates for the subject
        :return: None
        """
        assert(isinstance(subject, Subject))
        assert(isinstance(subject, tk.Widget))
        assert(callable(update_handler))
        self._subjects[subject]=update_handler
        return None
    
    def _detach_from_subjects(self):
        """
        Detach tkViewManager from all subjects (child widgets). Called from onDestroy(...).
        :return None:
        """
        for subject in self._subjects:
            subject.detach(self)
        return None

    def _CreateWidgets(self):
        """
        Abstract utility function to be called by __init__ to set up the child widgets of the tkViewManager widget.
        Must be implemented by children. Will raise NotImplementedError if called.
        :return None:
        """
        raise NotImplementedError
        return None

    def update(self, subject):
        """
        Implementation of Observer.update(). Acts as a switchboard based on which widget is notifying.
        :parameter subject: Which widget instance is notifying the mediator?
        :return None:
        """
        assert(isinstance(subject, Subject))
        # Call the updater for the subject argument after looking it up in the _subjects dictionary.
        self._subjects[subject]()
        return None

   
