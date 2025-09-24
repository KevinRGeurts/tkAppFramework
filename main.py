"""
The code in this modules __main__ illustrates how to a tkinter-based application. The demo application has one
widgets with a button. The button text cycles between 'Start' and 'Stop' when the button is clicked.
The demo application's menubar has the standard File | Exit menu item.

Exported Classes:
    DemoWidget -- A demo tkinter labelframe with a button that toggles between 'Start' and 'Stop' when clicked.
                  Also, a Subject for the DemotkViewManager to observe.
    DemotkViewManager -- Concrete implementation of tkViewManager that creates and manages a DemoWidget instace.
                         Also, an Observer of the DemoWidget.
    DemotkApp -- Concrete implementation of tkApp that creates a DemotkViewManager instance.

Exported Exceptions:
    None
 
Exported Functions:
    --main__ -- Create and launch tkinter-based Demo Application.
"""


# Standard
import tkinter as tk
from tkinter import ttk

# Local
from tkApp import tkApp
from tkViewManager import tkViewManager
from ObserverPatternBase import Subject


class DemoWidget(ttk.LabelFrame, Subject):
    """
    Class represents a tkinter label frame widget and is also a Subject in Observer design pattern.
    It has a button widget that will change it's text cyclicly from 'Start' to 'Stop' when clicked.
    """
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent, text='Demo Widget')
        Subject.__init__(self)
        
        btn = ttk.Button(self, command=self.OnButtonClicked)
        # Place button in grid and set weights for stretching the column and row in the grid
        # so that the demo widget resizes correctly.
        btn.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Create string variable which will be the text displayed on the button
        self._lbl=tk.StringVar()
        self._lbl.set('Start')
        btn['textvariable']=self._lbl
        
        self._is_started = False

    def get_state(self):
        """
        Return whether the widget's state is started or stopped. Returns this as a bool which is True if started,
        and False if NOT started (that is, stopped).
        :return _is_Started: True if started, False if stopped, bool
        """
        return self._is_started
    
    def OnButtonClicked(self):
        """
        Event handler for button click.
        :return None:
        """
        # Flip the started state
        if self._is_started:
            # Widget state is currently started, so change state to stopped
            self._is_started = False
            # Change button text to 'Start'
            self._lbl.set('Start')
        else:
            # Widget state is currently stopped, so change it's state to started
            self._is_started = True
            # Change button text to 'Stop'
            self._lbl.set('Stop')

        # Notify observers
        self.notify()

        return None


class DemotkViewManager(tkViewManager):
    """
    Provide an implementation of _CreateWidgets(...).
    """
    def _CreateWidgets(self):
        """
        Create the demo widget, register 
        :return None:
        """
        dw = DemoWidget(self)
        # Attach self as an observer of the subject demo widget
        dw.attach(self)
        # Register a handler function for updates from the subject demo widget
        self.register_subject(dw,self.handle_demo_widget_update)
        # Place demo widget in grid and set weights for stretching the column and row in the grid
        # so that the demo widget resizes correctly.
        dw.grid(column=0, row=0, sticky='NWES')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        return None

    def handle_demo_widget_update(self):
        """
        Handle updates from the demo widget:
        :return None:
        """
        print('Received update notification from DemoWidget')
        return None


class DemotkApp(tkApp):
    """
    Provide an implementation of _createViewManager(...) factory method.
    """
    def _createViewManager(self):
        """
        Concrete Implementation, which returns a DemotkViewManager instance.
        :return: tkViewManager instance that will be the app's view manager
        """
        return DemotkViewManager(self)


if __name__ == '__main__':
    
    """
    Create and launch tkinter-based DemotkApp.
    """
    
    # Create and configure the app
    root = tk.Tk()
    myapp = DemotkApp(root, title='Demo Application')

    # Start the app's event loop running
    myapp.mainloop()

     