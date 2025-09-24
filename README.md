# tkAppFramework

Source code: [GitHub](https://github.com/KevinRGeurts/tkAppFramework)
---
tkAppFramework is a Python library that facilitates the creation of a GUI application using tkinter. It provides
a base application class (tkApp), a base view manager class (tkViewManager), and a base class so that GUI widgets
managed by the view manager can act as observed subjects (Subject) in the Observer design pattern.

## tkApp class

tkApp is an abstract base class from which concrete tkinter applications can be derived.

Concrete implementation child classes must:
- Implement the factory method _createViewManager() to create and return a tkViewManager instance,
  which will create and manage the widgets of the application.
  
Concrete implementation child classes likely will:
- Extend __init__() to create and initialize any required business logic objects.
- Define and implement handler functions for menubar selections, beyond OnExit.

Concreate implementation child classes may:
- Extend _setup_child_widgets() if the tkViewManager does not create all of the app's widgets.

## tkViewManager class

tkViewManager is an abstract base class from which concrete view mangers for tkinter applications can be derived.
Concrete child implementations create widgets for tkApp concrete child implementations and handle the interactions
between widgets.

The tkViewManager class follows the Mediator design pattern and acts as Observer. tkViewManager is also a ttk.Frame.

Concrete implementation child classes must:
- Implement the method _CreateWidgets(), which is called by ```__init__(...)``` to create and set up the child widgets
  of the tkViewManager widget.
- Define and implement handler functions for widget updates, e.g., ```def handle_x_widget_update(self):```.
Notes:
- Handler functions are registered with the tkViewManager via ```register_subject(...)```, typically after each widget is created in ```_CreateWidgets()```. 
- Handler functions are automatically called from the ```update(...)``` method when a subject (child widget) notifies the tkViewManager by calling ```notify()``` on itself.

## Observer / Subject classes

The tkAppFramework also includes base classes for implementing the Observer design pattern. As described above,
tkViewManager is an Observer. Concrete child implementations of tkViewManager will typically observe one or more
child widgets, which are typically child implementations of tkinter.Labelframes and also Subjects.

### Observer class
Observer is a base class for all objects that will be an Observer in an Observer design pattern.
All Observer child classes must implement the ```update(...)``` method.

### Subject class
Subject is a base class for all objects that will be a Subject in an Observer design pattern.
Subjects should ```attach(...)``` and ```detach(...)``` Observers, and ```notify()``` them of changes in state.

## Usage
The code below shows a minimalist concrete implementation of tkApp and tkViewManager. The app is created and
launched.

```python
import tkinter as tk
from tkinter import ttk
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


# Create and configure the app
root = tk.Tk()
myapp = DemotkApp(root, title='Demo Application')

# Start the app's event loop running
myapp.mainloop()
```

## License
MIT License. See the LICENSE file for details
