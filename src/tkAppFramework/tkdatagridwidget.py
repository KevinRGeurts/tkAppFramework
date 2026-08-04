"""
This module defines a set of classes that together implement a "data grid widget".
This widget behaves a lot like an Excel spreadsheet. It can be used to display data records in a tabular format.
It can be used to collect input's from a user. It can be a hybrid where inputs and outputs are mixed in the same data grid.

Exported Classes:
    tkDataGridWidget -- It is a tkinter widget that uses a tkinter Canvas widget to display
                        data records and fields. It is a Subject in an Observer design pattern,
                        in anticipation of being observed by a tkViewManager.
    FieldType -- An IntEnum class that is used to specify the type of each field when configuring the tkDataGridWidget.
    FieldConfiguration -- A class that represents a field in data grid.
    DataGridUserAbilities -- A class that defines a set of "abilities" a user has within a tkDataGridWidget.
    DataGridAddRecordUpdateHint -- A hint passed by Subject.notify() to Observer.update(), indicating the a tkDataGridWidget has added a record.
    DataGridDeleteRecordUpdateHint -- A hint passed by Subject.notify() to Observer.update(), indicating that a tkDataGridWidget has deleted a record.
    DataGridChangedRecordUpdateHint -- A hint passed by Subject.notify() to Observer.update(), indicating that a tkDataGridWidget has changed the value/state of a field of a record.

    tkDGElement -- Class is the base class for classes that represent an element (cell) of a tkDataGridWidget. Class is a subject in Observer
                   design pattern, in anticipation of being observed by tkDataGridWidet class.
    tkDGElementBool -- Class represents a boolean element of a tkDataGridWidget, appearing as a Checkbutton widget.
    tkDGElementList -- Class represents a list (option menu) element of a tkDataGridWidget, appearing as an OptionMenu widget.
    tkDGElementText -- Class represents a text element of a tkDataGridWidget, appearing as an Entry widget.
    tkDGElementNumber -- Class represents a number element of a tkDataGridWidget, appearing as an Entry widget.
    tkDGElementFieldHeader -- Class represents a field header element of a tkDataGridWidget, appearing as an Entry widget.
                        
Exported Exceptions:
    tkDGElementTextInvalidEntryError - Raised when a tkDGElementText element's text is invalid for the field it represents.    
 
Exported Functions:
    _launch_help_app -- Launch tkinter app for displaying online help.

Logging:
    'tkDataGridWidget_logger' -- Logger for tkDataGridWidget module.
"""


# Standard imports
import logging
import tkinter as tk
from tkinter import font, filedialog
from tkinter import ttk
from tkinter.messagebox import showerror
from functools import partial
from enum import IntEnum
from os import getcwd
from multiprocessing import Process
import sysconfig
from math import isclose

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer, UpdateHint
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError
from tkAppFramework.uomsysadapter import UoMSysAdapter
from tkAppFramework.tkdgw_unitselect_dlg import tkUnitSelectDlg
from tkAppFramework.tkApp import tkHelpApp
from tkAppFramework.datagridfigurewidget import tkDataGridFigureWidget, DataGridFigureTemplate
from tkAppFramework.tkdgw_tooltip_tlw import tkTooltipWidget


# This function cannot be a method of tkDataGridWidget, due to Process using pickle.
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


# UpdateHint classes for tkDGElement.notify() to pass to tkDataGridWidget.update() method, to indicate what type of update has occurred and details about it.

class FieldHeaderElementTextUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating the a tkDGElementFieldHeader has had its
    raw text (the text that doesnt include ' (unit name)' changed.)
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            'prev_raw_state' specifies the original (previous) raw state (text) of the tkDGElementFieldHeader,
                             that is, the state excluding ' (unit name)', as string.
        """
        super().__init__(*args)
        self.prev_raw_state = kwargs.get('prev_raw_state')


class FieldHeaderElementUnitsUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating the a tkDGElementFieldHeader has had its
    units of measure changed.
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            'prev_unit_id' specifies the original (previous) unit ID of the tkDGElementFieldHeader, as Any
            'new_unit_id' specifies the newly set unit ID of the tkDGElementFieldHeader, as Any
        """
        super().__init__(*args)
        self.prev_unit_id = kwargs.get('prev_unit_id')
        self.new_unit_id = kwargs.get('new_unit_id')


class RecordElementValueUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating that a tkDGElement that is not a tkDGElementFieldHeader instance
    has had its value changed.
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            'prev_value' specifies the original (previous) value of the tkDGElement, as Any
            'new_value' specifies the newly set value of the tkDGElement, as Any
        """
        super().__init__(*args)
        self.prev_value = kwargs.get('prev_value')
        self.new_value = kwargs.get('new_value')


class RecordElementDefaultValueUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating that a tkDGElement that is not a tkDGElementFieldHeader instance
    has had its default value changed.
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            'prev_default_value' specifies the original (previous) default value of the tkDGElement, as Any
            'new_default_value' specifies the newly set default value of the tkDGElement, as Any
        """
        super().__init__(*args)
        self.prev_default_value = kwargs.get('prev_default_value')
        self.new_default_value = kwargs.get('new_default_value')


# the tkDGElement class and its child classes are the "elements" or cells of a tkDataGridWidget.

class tkDGElement(Subject):
    """
    Class is the base class for classes that represent an element of a tkDataGridWidget. Class is a subject in Observer
    design pattern, in anticipation of being observed by tkDataGridWidet class.
    """
    def __init__(self, observer=None, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter observer: Observer object that observes this tkDGElement object, assumed to be a tkDataGridWidget object
            Note: This is also the grandparent of the element widget, since the element widget is a child of a canvas that is a child of the tkDataGridWidget.
        :paramter x: The upper-left corner x-coordinate of the element in the data grid's canvas in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid's canvas in inches, as float
        :paramter w: The width of the element in the data grid's canvas in inches, as float
        :paramter h: The height of the element in the data grid's canvas in inches, as float
        """
        Subject.__init__(self)
        self.attach(observer)
        self._canvas_id = None # Required so that canvas ID is available in _create_element_widget() method,
                               # in case it is needed, for example in a partial for a widget command callback.
        # Create the element's control variable first, in case it is needed for creating the element widget, since the control variable might be used in the widget constructor.
        self._element_value = self._create_element_value()
        self._default_value = None
        self._element_widget = self._create_element_widget()
        self._setup_widget_bindings()
        # TODO: This is not OO, but don't see yet how to avoid it, since there is inconsistence between
        # widgets in how the control variable is bound to the widget.
        if type(self._element_widget) == tk.Entry:
           self._element_widget['textvariable'] = self._element_value
        elif type(self._element_widget) == tk.OptionMenu:
            # Constructor will have handled the binding of the control variable to the OptionMenu widget, so
            pass
        else:
           self._element_widget['variable'] = self._element_value
        self._canvas_id = observer.canvas.create_window(f"{x}i", f"{y}i", height=f"{h}i", width=f"{w}i",
                                                        anchor=tk.NW, window=self._element_widget)
        # Identifier returned by call to self._element_widget.after() to schedule a call to self._displayTooltip() method, or None if no call is scheduled.
        self._after_id = None
        self._tooltip_widget = None
    
    def _create_element_value(self):
        """
        Factory method to create the element widget's control variable. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: TThe control variable for the element widget, as tkinter variable object
        """
        raise NotImplementedError("The _create_element_widget() method must be implemented by child classes of tkDGElement.")
        return None        

    def _create_element_widget(self):
        """
        Factory method to create the element widget. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: The tkinter widget that is the element widget, as tkinter widget object
        """
        raise NotImplementedError("The _create_element_widget() method must be implemented by child classes of tkDGElement.")
        return None
    
    @property
    def elementWidget(self):
        return self._element_widget

    @property
    def canvasID(self):
        return self._canvas_id

    def get_state(self):
        """
        Get the state of the element.
        :return: Tuple (element type, element value), as (type, any)
        """
        value = None
        if self._element_value is not None:
            value = self._element_value.get()
        return (type(self), value)

    def get_default_value(self):
        """
        Get the default value for the element, which is used to reset the element to a default state when needed.
        :return: The default value for the element, as any (or None if no default value is set).
        """
        return self._default_value

    def set_state(self, value=None, hints=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        Note: Must be extended by child classes, because this base class implementation does nothing with value parameter.
              It does, however, call self.notify(), so when extending, call the base class implementation at the end of the extended method.
        :return: None
        """
        if hints is not None:
            self.notify(hints)
        else:
            self.notify()
        return None

    def clear_element_value(self, hints=None):
        """
        Clear the element value. Must be implemented by child classes, since the way to clear the value will depend on the type of element.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        Note: Must be extended by child classes, because this base class implementation does nothing with the element's value.
              It does, however, call self.notify(), so when extending, call the base class implementation at the end of the extended method.
        :return: None
        """
        if hints is not None:
            self.notify(hints)
        else:
            self.notify()
        return None

    def set_default_value(self, def_value):
        """
        Set the default value for the element, which is used to reset the element to a default state when needed.
        :parameter def_value: The default value for the element, as any (or None, if the element has no default value).)
        :return: None
        """
        _hint = RecordElementDefaultValueUpdateHint(prev_default_value=self._default_value, new_default_value=def_value)
        self._default_value = def_value
        self.notify([_hint])
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if self._element_widget is not None:
            if disabled:
                self._element_widget['state']=tk.DISABLED
            else:
                self._element_widget['state']=tk.NORMAL
        return None

    def _setup_widget_bindings(self):
        """
        Used to set up the tkinter event bindings for the element widget. Should be called in the child class
        constructors after the element widget is created.
        :return: None
        """
        if self._element_widget is not None:
            self._element_widget.bind('<FocusIn>', self.onFocusIn, add='+')
            self._element_widget.bind('<FocusOut>', self.onFocusOut, add='+')
            self._element_widget.bind('<KeyPress-Up>', self.onKeyPressUp, add='+')
            self._element_widget.bind('<KeyPress-Down>', self.onKeyPressDown, add='+')
            self._element_widget.bind('<KeyPress-Right>', self.onKeyPressRight, add='+')
            self._element_widget.bind('<KeyPress-Left>', self.onKeyPressLeft, add='+')
            self._element_widget.bind('<KeyPress-F3>', self.onKeyPressF3, add='+')
            self._element_widget.bind('<<ContextMenu>>', self.onContextMenu, add='+')
            self._element_widget.bind('<Enter>', self.onElementWidgetEnter, add='+')
            self._element_widget.bind('<Leave>', self.onElementWidgetLeave, add='+')
        return None

    def onElementWidgetEnter(self, event):
        """
        Handler for the Enter event. Initiate possible display of tooltip.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # Schedule a call to self._displayTooltip() method after 1 second (1000 miliseconds).
        # A tooltip should not be displayed immediately, but only after "hovering" in the element widget a short time.
        self._after_id = self._element_widget.after(1000, partial(self._displayTooltip, event))
        return None

    def onElementWidgetLeave(self, event):
        """
        Handler for the Leave event. Terminate display of or possible display of tooltip.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # If there is a displayed tooltip widget, destroy it.
        if self._tooltip_widget is not None:
            self._tooltip_widget.destroy()
        # If there is a scheduled call to self._displayTooltip() method, cancel it.
        # The assumption is that the mouse pointer has left the element widget after too short a time after entry to indicate
        # that a tooltip should be displayed.
        if self._after_id is not None:
            self._element_widget.after_cancel(self._after_id)
            self._after_id = None
        return None

    def _displayTooltip(self, event):
        """
        Display a tooltip for the element widget.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Tooltip to be displayed for tkDGElement with canvas ID {self.canvasID}.")
        # If there is a displayed tooltip widget, destroy it. This probably should not happen, but just in case.
        if self._tooltip_widget is not None:
            self._tooltip_widget.destroy()
        # Create a new tooltip widget and display it.
        tip_txt = self._getToolTipText()
        self._tooltip_widget = tkTooltipWidget(self._element_widget, text=tip_txt)
        self._tooltip_widget.show(event.x_root, event.y_root)
        return None

    def _getToolTipText(self):
        """
        Get the text to be displayed in the tooltip for the element widget.
        This method is intended can be extended/overriddenby child classes to provide specific tooltip text for the element widget.
        This version will return f"Value: {self.get_state()[1]}
                                   Default Value: {self.get_default_value()}"
            Note: If default value is None, it will not be included in the tooltip text.
        :return: The text to be displayed in the tooltip for the element widget, as string or None
            Note: Return None if no tooltip should be displayed.
        """
        tooltip_txt = f"Value: {self.get_state()[1]}"
        if self.get_default_value()is not None:
            tooltip_txt += f"\nDefault: {self.get_default_value()}"
        return tooltip_txt

    def onKeyPressF3(self, event):
        """
        Handler for F3 key press event. F3 key will restore the element's value to it's default, if
        one exists, set a BOOL element to False, or set a TEXT element to an emtpy string.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # Note that the Delete key alone should not be used for this purpose, since the Entry widget uses
        # the Delete key to edit the text in the entry widget.
        self._restoreDefaultValue()
        return None

    def _restoreDefaultValue(self):
        """
        Restore the element's value to it's default, if one exists.
        Note: If element is for a field that is read-only format, nothing is done.
        :return: None
        """
        # If the element is for a field that is read-only format, do nothing.
        if self._element_widget['state']!=tk.DISABLED and self._element_widget['state']!='readonly':
            _hints=[]
            if self._default_value is not None:
                _hints.append(RecordElementValueUpdateHint(prev_value=self._element_value.get(), new_value=self._default_value))
                self._element_value.set(self._default_value)
                self.notify(_hints)
            else:
                _prev_value = self._element_value.get()
                self.clear_element_value()
                # TODO: Confirm that should not notify on this branch because clear_element_value will handle it.
                # self.notify(_hints)
        return None

    def onContextMenu(self, event):
        """
        Handler for the <<ContextMenu>> virtual event. Call handler in element widget's grandparent tkDataGridWidget to
        handle the contextual menu.
        :parameter event: The tkinter event object for the <<ContextMenu>> virtual event
        :return: None
        """
        self._element_widget.focus_set()
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onContextMenu(event, self)
        return None

    def onFocusIn(self, event):
        """
        Handler for the FocusIn event. Call handler in element widget's grandparent tkDataGridWidget to
        update it's tracking of currently focused element to this element widget.
        :parameter event: The tkinter event object for the FocusIn event
        :return: None
        """
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onFocusIn(self)
        return None

    def onFocusOut(self, event):
        """
        Handler for the FocusOut event. Call handler in element widget's grandparent tkDataGridWidget to
        update it's tracking of currently focused element to None.
        :parameter event: The tkinter event object for the FocusOut event
        :return: None
        """
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onFocusOut(self)
        return None

    def onKeyPressDown(self, event):
        """
        Handler for the down-arrow key press event. Call handler in element widget's grandparent tkDataGridWidget to
        move focus to the element widget below the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onKeyPressDown(event)
        return None

    def onKeyPressUp(self, event):
        """
        Handler for the up-arrow key press event. Call handler in element widget's grandparent tkDataGridWidget to
        move focus to the element widget above the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"KeyPress-Up event received from tkDGElement with canvas ID {self.canvasID}.")
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onKeyPressUp(event)
        return None

    def onKeyPressRight(self, event):
        """
        Handler for the right-arrow key press event. Call handler in element widget's grandparent tkDataGridWidget to
        move focus to the element widget to the right of the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onKeyPressRight(event)
        return None

    def onKeyPressLeft(self, event):
        """
        Handler for the left-arrow key press event. Call handler in element widget's grandparent tkDataGridWidget to
        move focus to the element widget to the left of the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # Note: First master is the canvas, second master is the tkDataGridWidget
        self._element_widget.master.master.onKeyPressLeft(event)
        return None


class tkDGElementBool(tkDGElement):
    """
    Class represents a boolean element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter parent: tkinter widget that will be the parent of the element's widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        """
        super().__init__(parent, x, y, w, h)

    def _create_element_value(self):
        """
        Factory method to create the element widget's control variable. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: TThe control variable for the element widget, as tkinter variable object
        """
        control_var = tk.IntVar()
        return control_var

    def _create_element_widget(self):
        """
        Factory method to create the tk.Checkbutton element widget.
        :return: The tkinter widget that is the element widget, as tkinter widget object
        """
        widget = tk.Checkbutton(self._observers[0].canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                                takefocus=1, command=partial(self.onCheckbuttonClicked, self._canvas_id) )
        return widget

    def onCheckbuttonClicked(self, canvas_id):
        """
        Called when a Checkbutton is clicked.
        :parameter canvas_id: The canvas ID of the element widget that was clicked, as int
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Checkbutton with canvas ID {canvas_id} was clicked.")
        self._element_widget.focus_set()
        # Call set_state() so that notify gets called
        new_value = self.get_state()[1]
        self.set_state(new_value)
        return None

    def get_state(self):
        """
        Get the state of the element.
        :return: Tuple (element type, element value), as (type, boolean)
        """
        value = None
        if self._element_value is not None:
            value = self._element_value.get()
        return (type(self), bool(value))

    def set_state(self, value=None, hints=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element, as boolean
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        assert(type(value)==bool)
        _hints=hints
        if _hints is None:
            _hints=[]
        _hints.append(RecordElementValueUpdateHint(prev_value=self.get_state()[1], new_value=value))
        self._element_value.set(int(value))
        super().set_state(hints=_hints) # So notify() gets called.
        return None

    def clear_element_value(self, hints=None):
        """
        Clear the element value, by setting it to False.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        self.set_state(False, hints)
        # DON'T call super().clear_element_value(), because set_state() already calls notify().
        return None


class tkDGElementList(tkDGElement):
    """
    Class represents a list (option menu) element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter parent: tkinter widget that is the parent of this widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        """
        super().__init__(parent, x, y, w, h)        

    def _create_element_value(self):
        """
        Factory method to create the element widget's control variable. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: TThe control variable for the element widget, as tkinter variable object
        """
        control_var = tk.StringVar()
        return control_var

    def _create_element_widget(self):
        """
        Factory method to create the tk.OptionMenu element widget.
        :return: The tkinter widget that is the element widget, as tkinter widget object
        """
        widget = tk.OptionMenu(self._observers[0].canvas, self._element_value, '')
        # Use configure to set the options for the OptionMenu, since the constructor does not allow setting all of the desired options.
        widget.configure(relief="flat", takefocus=1)
        return widget

    def onOptionSelected(self, canvas_id, option):
        """
        Called when an OptionMenu selection is made.
        :parameter canvas_id: The canvas ID of the element widget that had an option selected, as int
        :paramter option: The option selected, as string
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"OptionMenu with canvas ID {canvas_id} had option {option} selected.")
        self.set_state(option)
        self._element_widget.focus_set()
        return None

    def set_state(self, value=None, hints=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        assert(type(value)==str)
        # TODO: Check that value is in the list of options for the OptionMenu.
        _hints=hints
        if _hints is None:
            _hints=[]
        _hints.append(RecordElementValueUpdateHint(prev_value=self.get_state()[1], new_value=value))
        self._element_value.set(value)
        super().set_state(hints=_hints)
        return None

    def clear_element_value(self, hints=None):
        """
        Clear the element value. Actually this does nothing, since there is no clear value for an OptionMenu, but method must be implemented since it is abstract in the base class.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        # Note. super().clear_element_value() is not called, since no change to the value is made.
        return None

    def set_menu_choices(self, choices):
        """
        Set the choices for the OptionMenu element widget.
        :parameter choices: The choices to set for the OptionMenu, as tuple of strings
        """
        assert(type(choices)==tuple)
        # See: https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        self._element_value.set('')
        self._element_widget['menu'].delete(0, 'end')
        for choice in choices:
            self._element_widget['menu'].add_command(label=choice, command=tk._setit(self._element_value, choice,
                                                                                     callback=partial(self.onOptionSelected, self._canvas_id) ) )
        self.set_state(choices[0])
        return None


class tkDGElementText(tkDGElement):
    """
    Class represents a text containing element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter parent: tkinter widget that is the parent of this widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        """
        super().__init__(parent, x, y, w, h)

        # Register the OnEntryChanged and OnInvalidEntryChange methods with tkinter.
        OnEntryChangedCommand = self._element_widget.register(partial(self.OnEntryChanged, self._canvas_id))
        OnInvalidEntryChangeCommand = self._element_widget.register(self.OnInvalidEntryChange)
        # Congigure the Entry widget to call the appropriate method when a change is made to the text entry.
        self._element_widget.configure(validatecommand=OnEntryChangedCommand)
        self._element_widget.configure(invalidcommand=OnInvalidEntryChangeCommand)

    def _create_element_value(self):
        """
        Factory method to create the element widget's control variable. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: TThe control variable for the element widget, as tkinter variable object
        """
        control_var = tk.StringVar()
        return control_var

    def _create_element_widget(self):
        """
        Factory method to create the tk.Entry element widget.
        :return: The tkinter widget that is the element widget, as tkinter widget object
        """
        widget = tk.Entry(self._observers[0].canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                          takefocus=1, validate='focusout')
        return widget

    def _setup_widget_bindings(self):
        """
        Used to extend the set up the tkinter event bindings for the text element widget.
        :return: None
        """
        super()._setup_widget_bindings()
        if self._element_widget is not None:
            self._element_widget.bind('<KeyPress-Return>', self.onKeyPressReturnEnter, add='+')
            self._element_widget.bind('<KeyPress-KP_Enter>', self.onKeyPressReturnEnter, add='+')
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if self._element_widget is not None:
            if disabled:
                # So text content can still be selected and copied, but not changed.
                self._element_widget['state']='readonly'
            else:
                self._element_widget['state']=tk.NORMAL
        return None

    def onKeyPressReturnEnter(self, event):
        """
        Handler for the Return and key pad Enter key press events.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        self.OnEntryChanged(self._canvas_id)
        return None

    # TODO: Modify logic to make this more parallel to numeric element, where set_state is called. In particular, 
    # want notify() to be called differently so it has a record element value change hint.
    def OnEntryChanged(self, canvas_id):
        """
        Event handler for changes to text entry.
        :parameter canvas_id: The canvas ID of the element widget into which text was entered, as int
        :return True: if text entry change is valid, False if invalid, boolean
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Entry with canvas ID {canvas_id} was changed.")
        # First test entry validity based on any validator associates with this element's field configuration.
        # Note: First master is the canvas, second master is the tkDataGridWidget
        owning_dgw = self._element_widget.master.master
        (field_name, record_index) = owning_dgw._get_element_coords(self)
        field_config = [fc for fc in owning_dgw._fields_config if fc.fieldName==field_name]
        _proposed_entry = self._element_value.get()
        if len(field_config) > 0:
            field_config = field_config[0]
            validator = field_config.fieldValidator
            if validator is not None:
                try:
                    validator(proposed_entry = _proposed_entry)
                except tkDGElementTextInvalidEntryError as e:
                    showerror(title='Data Grid Text Entry Error', message=e.args[0], parent=self._element_widget.master)
                    return False
        # Inform all observers of the change in the text entry
        try:
            # Validity here is still only an assumption. Observer(s) could raise exception if they have
            # a problem with the new entry value when notify() is called, and OnInvalidEntryChange() will correct to False.
            if (_proposed_entry is not None):
                self.set_state(_proposed_entry)
            return True
        except tkDGElementTextInvalidEntryError as e:
            showerror(title='Data Grid Text Entry Error', message=e.args[0], parent=self._element_widget.master)
            return False

    def OnInvalidEntryChange(self):
        """
        Called when OnEntryChanged returns False.
        :return None:
        """
        # Keep focus on the Entry widget, so that user can correct the invalid entry.
        self._element_widget.focus_set()
        self.notify()
        return None

    def set_state(self, value=None, hints=None):
        """
        Set the state of the text element.
        :paramter value: The value to set in the element.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        assert(type(value)==str)
        _hints=hints
        if _hints is None:
            _hints=[]
        _hints.append(RecordElementValueUpdateHint(prev_value=self.get_state()[1], new_value=value))
        self._element_value.set(value)
        super().set_state(hints=_hints)
        return None

    def clear_element_value(self, hints=None):
        """
        Clear the element value, by setting it to ''.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        self.set_state('', hints)
        # DON"T call super().clear_element_value(), as set_state() already calls notify().
        return None


class tkDGElementFieldHeader(tkDGElement):
    """
    Class represents a field header element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25, field_config=None):
        """
        :parameter parent: tkinter widget that is the parent of this widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        :parameter field_config: The field configuration this field header is associated with, as FieldConfiguration object
        """
        super().__init__(parent, x, y, w, h)
        self._raw_state = '' # The state without any units, i.e., without the ' (unit name)' part.
        assert(isinstance(field_config, FieldConfiguration))
        self._field_config = field_config

    def _create_element_value(self):
        """
        Factory method to create the element widget's control variable. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: TThe control variable for the element widget, as tkinter variable object
        """
        control_var = tk.StringVar()
        return control_var

    def _create_element_widget(self):
        """
        Factory method to create the tk.Entry element widget.
        :return: he tkinter widget that is the element widget, as tkinter widget object
        """
        widget = tk.Entry(self._observers[0].canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                          takefocus=0, validate='focusout')
        return widget

    def _setup_widget_bindings(self):
        """
        Used to extend the set up the tkinter event bindings for the field header element widget.
        :return: None
        """
        super()._setup_widget_bindings()
        if self._element_widget is not None:
            self._element_widget.bind('<Double-1>', self.onDoubleClickBtn1, add='+')
        return None

    def onDoubleClickBtn1(self, event):
        """
        Handler for mouse button 1 double-click events.
        :parameter event: The tkinter event object for the mouse button 1 double-click event
        :return: None
        """
        if self._field_config.fieldUnitGroup is not None:
            # Display the unit selection dialog
            # Note: First master is the canvas, second master is the tkDataGridWidget
            dgw = self._element_widget.master.master
            tkUnitSelectDlg(dgw, uom_adapter=dgw.uomAdapter, quantity_name=self._raw_state,
                            unit_group_id=self._field_config.fieldUnitGroup, initial_unit_id=self._field_config.fieldUnitID,
                            initial_unit_name=self._field_config.fieldUnitName, apply_callback=self.set_units)
            # Note: If dialog is "Okayed" then apply_callback will have been called to set units.
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if self._element_widget is not None:
            if disabled:
                # So text content can still be selected and copied, but not changed.
                self._element_widget['state']='readonly'
            else:
                self._element_widget['state']=tk.NORMAL
        return None

    def set_state(self, value=None, hints=None):
        """
        Set the state of the text element.
        :paramter value: The raw (without unit name) value to set in the element.
        :parameter hints: An optional list of hints to pass to Observer.update() to specify what types of 
                          update have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        assert(type(value)==str)
        if self._raw_state != value:
            _hint = FieldHeaderElementTextUpdateHint(prev_raw_state = self._raw_state)
            if hints is not None:
                hints.append(_hint)
            else:
                hints = [_hint]
        self._raw_state = value
        if (self._field_config.fieldUnitGroup is not None) and (self._field_config.fieldUnitID is not None) and (len(self._field_config.fieldUnitName)>0):
            self._element_value.set(f"{value} ({self._field_config.fieldUnitName})")
        else:
            self._element_value.set(value)
        super().set_state(hints=hints)
        return None

    def clear_element_value(self, hints=None):
        """
        Clear the element value, by setting it to ''.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        self.set_state('', hints)
        # DON'T call super().clear_element_value(), because set_state() already calls notify().
        return None

    def set_units(self, unit_group_id=None, unit_id=None, unit_name=''):
        """
        :parameter unit_group_id: The ID of the unit group of the element, as Any or None
            Note: Only once can the unit_group_id not be None
        :parameter unit_id: The ID of the unit of the element, as Any or None
        :parameter unit_name: The name of the unit of the element, as string (could be '')
        :return: None
        """
        #TODO: This code will result in an exception down the call stack if the unitID is the same as the previous unitID, but the unitName is different.
        # This should not happen.
        assert(isinstance(unit_name, str))
        _hint = None
        if self._field_config.fieldUnitID is not None:
            if unit_id != self._field_config.fieldUnitID:
                _hint = FieldHeaderElementUnitsUpdateHint(prev_unit_id=self._field_config.fieldUnitID, new_unit_id=unit_id)
        self._field_config.fieldUnitID = unit_id
        if unit_name != self._field_config.fieldUnitName:
            self._field_config.fieldUnitName = unit_name
            # Force a change in the units displayed in the element's text widget
            self.set_state(self._raw_state, [_hint]) 
        return None


class tkDGElementNumber(tkDGElement):
    """
    Class represents a number (float or int) containing element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter parent: tkinter widget that is the parent of this widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        """
        super().__init__(parent, x, y, w, h)
        # IFF tkDataGridWidget HAS a uom adapter, then self._numeric_value will be in base units,
        # and the element's text entry will be in the units specified by the field configuration for this element.
        # The default value for the element will also be in base units.
        self._numeric_value = None
        # Register the OnEntryChanged and OnInvalidEntryChange methods with tkinter.
        OnEntryChangedCommand = self._element_widget.register(partial(self.OnEntryChanged, self._canvas_id))
        OnInvalidEntryChangeCommand = self._element_widget.register(self.OnInvalidEntryChange)
        # Congigure the Entry widget to call the appropriate method when a change is made to the text entry.
        self._element_widget.configure(validatecommand=OnEntryChangedCommand)
        self._element_widget.configure(invalidcommand=OnInvalidEntryChangeCommand)

    def _create_element_value(self):
        """
        Factory method to create the element widget's control variable. Must be implemented by child classes.
        Will raise NotImplementedError if called from the base class, since it must be implemented by child classes.
        :return: TThe control variable for the element widget, as tkinter variable object
        """
        control_var = tk.StringVar()
        return control_var

    def _create_element_widget(self):
        """
        Factory method to create the tk.Entry element widget.
        :return: The tkinter widget that is the element widget, as tkinter widget object
        """
        widget = tk.Entry(self._observers[0].canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                          takefocus=1, validate='focusout')
        return widget

    def _setup_widget_bindings(self):
        """
        Used to extend the set up the tkinter event bindings for the Number element widget.
        :return: None
        """
        super()._setup_widget_bindings()
        if self._element_widget is not None:
            self._element_widget.bind('<KeyPress-Return>', self.onKeyPressReturnEnter, add='+')
            self._element_widget.bind('<KeyPress-KP_Enter>', self.onKeyPressReturnEnter, add='+')
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if self._element_widget is not None:
            if disabled:
                # So text content can still be selected and copied, but not changed.
                self._element_widget['state']='readonly'
            else:
                self._element_widget['state']=tk.NORMAL
        return None

    def onKeyPressReturnEnter(self, event):
        """
        Handler for the Return and key pad Enter key press events.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        self.OnEntryChanged(self._canvas_id)
        return None

    def onKeyPressF3(self, event):
        """
        Handler for the F3 key press event. F3 key will restore the element's value to it's default, if
        one exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Request to restore default of Entry with canvas ID {self._canvas_id}.")
        # If the element is for a field that is read-only format, do nothing.
        if self._element_widget['state']!=tk.DISABLED and self._element_widget['state']!='readonly':
            if self._default_value is not None:
                default_value = self._default_value
                self.set_state(default_value)
            else:
                self.clear_element_value()
        return None

    def OnEntryChanged(self, canvas_id):
        """
        Event handler for changes to Number entry.
        :parameter canvas_id: The canvas ID of the element widget into which text was entered, as int
        :return True: if text entry change is valid, False if invalid, boolean
        """
        # On entering this method, self._element_value.get() will return a string of text that, if a number,
        # is in the current units for the field associated with this element, if that field has a unit group.
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Entry with canvas ID {canvas_id} was changed.")
        # First test entry validity based on any validator associates with this element's field configuration.
        # Note: First master is the canvas, second master is the tkDataGridWidget
        owning_dgw = self._element_widget.master.master
        (field_name, record_index) = owning_dgw._get_element_coords(self)
        field_config = [fc for fc in owning_dgw._fields_config if fc.fieldName==field_name]
        _proposed_entry = self._element_value.get()
        if len(field_config) > 0:
            field_config = field_config[0]
            validator = field_config.fieldValidator
            if validator is not None:
                try:
                    # TODO: The validator needs to handle unit conversions, otherwise error messages for min/max violations aren't meaningful.
                    validator(proposed_entry = _proposed_entry)
                except tkDGElementTextInvalidEntryError as e:
                    showerror(title='Data Grid Number Entry Error', message=e.args[0], parent=self._element_widget.master)
                    return False
        # Inform all observers of the change in the number entry
        try:
            # Validity here is still only an assumption. Observer(s) could raise exception if they have
            # a problem with the new entry value when notify() is called from set_state().
            if (_proposed_entry is not None) and (len(_proposed_entry)>0):
                value = float(_proposed_entry) # Current units, as float
                # Note: First master is the canvas, second master is the tkDataGridWidget
                owning_dgw = self._element_widget.master.master
                # Convert value to base units, if the field associated with this element has a unit group.
                if owning_dgw._element_has_units(self):
                    # Convert to base units
                    (field_name, record_index) = owning_dgw._get_element_coords(self)
                    current_uid = owning_dgw.get_field_unitID(field_name)
                    ugrpid = owning_dgw.get_field_unit_group(field_name)
                    base_uid = owning_dgw.uomAdapter.get_base_unit_id_for_unit_group(ugrpid)
                    value = owning_dgw.uomAdapter.convert(from_unit_id=current_uid, to_unit_id=base_uid, value=value)
                self.set_state(value)
            else:
                self.set_state(None)
            return True
        except tkDGElementTextInvalidEntryError as e:
            showerror(title='Data Grid Text Entry Error', message=e.args[0], parent=self._element_widget.master)
            return False

    def OnInvalidEntryChange(self):
        """
        Called when OnEntryChanged returns False.
        :return None:
        """
        # Keep focus on the Entry widget, so that user can correct the invalid entry.
        self._element_widget.focus_set()
        # TODO: Reseacch if this notify is needed.
        self.notify()
        return None

    def set_state(self, value=None, hints=None):
        """
        Set the state of the number element.
        :paramter value: The numeric value to set in the element, as float|int|None
            Note: If the number element is associated with a field that has a unit group, then value parameter is assumed to be in the base units for the field.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]        
        :return: None
        """
        # As we enter this method, the following should be true if the number element is associated with a field that
        # has a unit group.
        # (1) self._numeric_value is in base units, and
        # (2) value parameter is in base units, and
        # (3) self._default_value is in base units
        # (4) The control variable self._element_value is a string that is in the current units for the field associated with this element.
        assert((value is None) or (type(value)==float) or (type(value)==int))

        _hints=hints
        if _hints is None:
            _hints=[]
        
        # Note: First master is the canvas, second master is the tkDataGridWidget
        owning_dgw = self._element_widget.master.master
        
        value_current_units = value
        # Convert value parameter to current units, if the field associated with this element has a unit group.
        if owning_dgw._element_has_units(self) and value_current_units is not None:
            # Convert value_current_units to current units
            (field_name, record_index) = owning_dgw._get_element_coords(self)
            current_uid = owning_dgw.get_field_unitID(field_name)
            ugrpid = owning_dgw.get_field_unit_group(field_name)
            base_uid = owning_dgw.uomAdapter.get_base_unit_id_for_unit_group(ugrpid)
            value_current_units = owning_dgw.uomAdapter.convert(from_unit_id=base_uid, to_unit_id=current_uid, value=value_current_units)
        
        # First, handle the text displayed in the Entry widget, by changing the control variable.
        
        old_txt_val = self._element_value.get() # In current units, as string
        if len(old_txt_val) > 0: # In case the Entry widget is empty, don't try to convert to float.
            old_value = float(self._element_value.get()) # In current units, as float
        else: # Instead "convert" it to None, so that the comparison below will be correct.
            old_value = None
        if not self._fuzzy_compare(value_current_units, old_value, rel_tol=1e-8):
            if value is None:
                self._element_value.set('')
            else:
                self._element_value.set(self._format_value(value_current_units))

        # Second, handle the numeric value stored in self._numeric_value.

        old_value = self._numeric_value
        # Only set the value and notify observers if the value has actually changed, to avoid unnecessary updates.
        if not self._fuzzy_compare(value, old_value, rel_tol=1e-8):
            _hints.append(RecordElementValueUpdateHint(prev_value=old_value, new_value=value))
            self._numeric_value = value
            self.notify(_hints)
        return None

    def _fuzzy_compare(self, value1, value2, rel_tol=1e-8):
        """
        Compare two float or int values for equality, with a relative tolerance. This extends math isclose() to handle
        None values in a way that is useful for this class.
        :parameter value1: The first value to compare, as float or int
        :parameter value2: The second value to compare, as float or int
        :parameter rel_tol: The relative tolerance for the comparison, as float
        :return: True if the values are equal within the specified relative tolerance, False otherwise, boolean
        """
        if value1 is not None:
            assert(isinstance(value1, int) or isinstance(value1, float))
        if value2 is not None:
            assert(isinstance(value2, int) or isinstance(value2, float))
        if value1 is None and value2 is None:
            # Both are None
            return True
        elif value1 is None or value2 is None:
            # One is None and the other is not
            return False
        else:
            # Both are not None
            return isclose(value1, value2, rel_tol=rel_tol)

    def _format_value(self, value):
        """
        This utility function applies logic to format a float or int value as a string, so that scientific notation is
        used if the number is particularly small or large.
        :parameter value: The value to format, as float or int
        :return: The formatted value as a string
        """
        assert(isinstance(value, int) or isinstance(value, float))
        formatted_value = '{:.8G}'.format(value)
        return formatted_value

    def clear_element_value(self, hints=None):
        """
        Clear the element value, by setting it to None.
        :parameter hints: An optional list of hints passed to observers to specify what types of 
                          updates have occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return: None
        """
        self.set_state(None, hints)
        # DON"T call super().clear_element_value(), as set_state() already calls notify().
        return None

    def get_state(self):
        """
        Get the state of the number element.
        :return: Tuple (element type, element value), as (type, int|float|None)
            Note: The returned value will be in base units if the number element is associated with a field that has a unit group.
        """
        value = self._numeric_value
        return (type(self), value)

    def _getToolTipText(self):
        """
        Get the text to be displayed in the tooltip for the element widget.
        This version will return f"Value: {self.get_state()[1]} ({<display units>})\n
                                   Default Value: {self.get_default_value()} ({<display units>})"
            Notes: (1) If default value is None, it will not be included in the tooltip text.
                   (2) Value and Default Value will be displayed in display units.
        :return: The text to be displayed in the tooltip for the element widget, as string or None
            Note: Return None if no tooltip should be displayed.
        """
        (disp_val, disp_units) = self.get_value_in_display_units()
        (disp_def_val, disp_def_units) = self.get_default_value_in_display_units()

        tooltip_txt = f"Value: {disp_val} ({disp_units})"
        if self.get_default_value()is not None:
            tooltip_txt += f"\nDefault: {disp_def_val} ({disp_def_units})"
        return tooltip_txt

    def get_value_in_display_units(self):
        """
        Get the value of the number element in current display units, and the unit name for the current display units.
        :return: (Value of the number element in current display units, Display unit name,  as (float, string)
            Note: If the number element is NOT associated with a field that has a unit group,
                  then the value will returned in base units and the unit name will be ''.
        """
        ret_elem_val = None
        ret_elem_units = ''
        # Note: First master is the canvas, second master is the tkDataGridWidget
        owning_dgw = self._element_widget.master.master
        
        ret_elem_val = self.get_state()[1]
        # Convert elements value from base to current units, if the field associated with this element has a unit group.
        if owning_dgw._element_has_units(self) and ret_elem_val is not None:
            # Convert value_current_units to current units
            (field_name, record_index) = owning_dgw._get_element_coords(self)
            current_uid = owning_dgw.get_field_unitID(field_name)
            ugrpid = owning_dgw.get_field_unit_group(field_name)
            base_uid = owning_dgw.uomAdapter.get_base_unit_id_for_unit_group(ugrpid)
            ret_elem_val = owning_dgw.uomAdapter.convert(from_unit_id=base_uid, to_unit_id=current_uid, value=ret_elem_val)
            ret_elem_units = owning_dgw.get_field_unit_name(field_name)

        return (ret_elem_val, ret_elem_units)

    def get_default_value_in_display_units(self):
        """
        Get the default value of the number element in current display units, and the unit name for the current display units.
        :return: (Default value of the number element in current display units, Display unit name,  as (float, string)
            Note: If the number element is NOT associated with a field that has a unit group,
                  then the default value will returned in base units and the unit name will be ''.
        """
        ret_elem_val = None
        ret_elem_units = ''
        # Note: First master is the canvas, second master is the tkDataGridWidget
        owning_dgw = self._element_widget.master.master
        
        ret_elem_val = self.get_default_value()
        # Convert elements value from base to current units, if the field associated with this element has a unit group.
        if owning_dgw._element_has_units(self) and ret_elem_val is not None:
            # Convert value_current_units to current units
            (field_name, record_index) = owning_dgw._get_element_coords(self)
            current_uid = owning_dgw.get_field_unitID(field_name)
            ugrpid = owning_dgw.get_field_unit_group(field_name)
            base_uid = owning_dgw.uomAdapter.get_base_unit_id_for_unit_group(ugrpid)
            ret_elem_val = owning_dgw.uomAdapter.convert(from_unit_id=base_uid, to_unit_id=current_uid, value=ret_elem_val)
            ret_elem_units = owning_dgw.get_field_unit_name(field_name)

        return (ret_elem_val, ret_elem_units)


# Classes for configuring the fields and allowed abilities of a tkDataGridWidget

class FieldType(IntEnum):
    """
    This IntEnum class is used to specify the type of each field when configuring the tkDataGridWidget.
    It actually makes sense to use an Enum here, so that clients do not need to know about the hierarchy of
    tkDGElement classes to specify field types.
    """
    BOOL = 1
    LIST = 2
    TEXT = 3
    NUMBER = 4
    # Add more field types as needed


class FieldConfiguration:
    """
    This class represents a field in data grid.
    """
    def __init__(self, name='', field_type=FieldType.TEXT, field_format='', validator=None, unit_group=None,
                 unit_id=None, unit_name=''):
        """
        :parameter name: The name of the data field, as string
        :parameter field_type: The type of the data field, as FieldType Enum value
        :parameter field_format: A string that is the key to looking up a format in the element format dictionary
                                 maintained by a tkDataGridWidget, as string
            Note: The value in the element format dictionary is used to format the element widgets for the records of the field.
        :parameter validator: Callable that takes in a value for the field and raises a tkDGElementTextInvalidEntryError if the value is invalid for the field,
                              or does nothing if the value is valid for the field. Set to None if there is no validation for the field,
                              or if the field is not a TEXT field. As callable|None
        :parameter unit_group: The unit group ID for the field, or None if not applicable, as Any|None
        :parameter unit_id: The current unit ID for the field, or None if not applicable, as Any|None
        :parameter unit_name: The current unitname for the field, as string ('' if not applicable)
        """
        self._field_name = name
        self._field_type = field_type
        self._field_format = field_format
        self._field_validator = validator
        self._field_unit_group = unit_group
        self._field_unit_id = unit_id
        self._field_unit_name = unit_name

    @property
    def fieldName(self):
        return self._field_name

    @property
    def fieldType(self):
        return self._field_type

    @property
    def fieldFormat(self):
        return self._field_format

    @property
    def fieldValidator(self):
        return self._field_validator

    @property
    def fieldUnitGroup(self):
        return self._field_unit_group

    @property
    def fieldUnitID(self):
        return self._field_unit_id

    @fieldUnitID.setter
    def fieldUnitID(self, value):
        self._field_unit_id = value

    @property
    def fieldUnitName(self):
        return self._field_unit_name

    @fieldUnitName.setter
    def fieldUnitName(self, value):
        self._field_unit_name = value


class DataGridUserAbilities:
    """
    This class defines a set of "abilities" a user has within a tkDataGridWidget. Currently it is used to
    disable options on the contextual menu which should not be available to the user. For example, for most
    applications with a tkDataGridWidget, the ability to delete a field should NOT be available.
    """
    def __init__(self, can_insert_field=False, can_delete_field=False, can_insert_record=False, can_delete_record=False):
        """
        """
        assert(isinstance(can_insert_field, bool))
        assert(isinstance(can_delete_field, bool))
        assert(isinstance(can_insert_record, bool))
        assert(isinstance(can_delete_record, bool))
        self._can_insert_field = can_insert_field
        self._can_delete_field = can_delete_field
        self._can_insert_record = can_insert_record
        self._can_delete_record = can_delete_record


# UpdateHint classes for tkDataGridWidget.notify() to pass to <client>.update() method, to indicate what type of update has occurred and details about it.

class DataGridAddRecordUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating the a tkDataGridWidget has added a record.
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            'new_record_index' specifies the index of the new record in the data grid, as int
        """
        super().__init__(*args)
        self.new_record_index = kwargs.get('new_record_index')


class DataGridDeleteRecordUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating that a tkDataGridWidget has deleted a record.
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            'deleted_record_index' specifies the index of the deleted record in the data grid, as int
        """
        super().__init__(*args)
        self.deleted_record_index = kwargs.get('deleted_record_index')


class DataGridChangedRecordUpdateHint(UpdateHint):
    """
    A hint passed by Subject.notify() to Observer.update(), indicating that a tkDataGridWidget has changed a field of a record.
    """
    def __init__(self, *args, **kwargs):
        """
        Expected kwargs:
            '_record_index' specifies the index of the deleted record in the data grid, as int
        """
        super().__init__(*args)
        self.changed_record_index = kwargs.get('changed_record_index') # integer
        self.changed_record_field = kwargs.get('changed_record_field') # string


# The main class for the data grid widget

class tkDataGridWidget(Subject, Observer, ttk.Labelframe):
    """
    Class represents a tkinter label frame, the widget contents of which allow displayinbg and interacting with
    data records and fields. Class is a Subject in Observer design pattern so that it can be observed by a tkViewManager object.
    Class is an Observer in Observer design pattern so that it can observe tkDGElement objects.
    """
    # TODO: Pass in row heights and collumn widths?
    def __init__(self, parent, title='Data Grid', fields_config=[], num_records=0, log_level = logging.INFO,
                 uom_adapter = None, fields_are_cols = True, user_abilities = DataGridUserAbilities()) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter title: The text label of the Labelframe, as string
        :parameter fields_config: List of FieldConfiguraton objects specifying the configuration of each field in the data grid,
                                  as [FieldConfiguration object]
        :parameter num_records: The number of records to display in the data grid, as int
        :parameter log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        :parameter uom_adapter: The Units of Measure System Adapter to be used by the data grid, as UoMSysAdapter object or None
        :parameter fields_are_cols: True if the fields are the columns in the grid. False if the fields are the rows
                                    in the grid. Only True is currently supported. As boolean.
        :parameter user_abilities: Controls abilities a user has using contextual menu, as DataGridUserAbilities object
        """
        Subject.__init__(self)
        Observer.__init__(self)
        ttk.Labelframe.__init__(self, parent, text=title, takefocus=tk.TRUE)

        # Set up logging for this class.
        self._setup_logging(log_level)

        assert(isinstance(fields_are_cols, bool))
        self._fields_are_cols = fields_are_cols

        if uom_adapter is not None:
            assert(isinstance(uom_adapter, UoMSysAdapter))
        self._uom = uom_adapter

        assert(isinstance(user_abilities, DataGridUserAbilities))
        self._user_abilities = user_abilities

        # Dictionary of element format configurations, where Key=format name as string, Value=configuration tuple (text color, cell color, read only, default cell color), as (string, (string, string, boolean, string))
        # Hex RGB color source: https://color-register.org
        self._element_formats = {}
        # default_cell_color = "Microsoft Green"
        self.create_element_format(format_name='field_header', text_color='black', cell_color='#808080', read_only=True)
        self.create_element_format(format_name='editable', text_color='black', cell_color='white', read_only=False)
        self.create_element_format(format_name='read_only', text_color='black', cell_color='cyan', read_only=True)

        # Add a binding for window destruction, so that this tkDataGridWidget can detach itself from its subjects when it is destroyed.
        self.bind('<Destroy>', self.onDestroy, '+')

        # Store fields and records configuraton info as class attributes.
        assert(type(num_records)==int)
        self._num_records = num_records
        assert(type(fields_config)==list)
        for fc in fields_config:
            assert(isinstance(fc, FieldConfiguration))
        self._fields_config = fields_config

        # Store the tkDGElementFieldHeader widgets in the data grid in a list.
        self._header_elements = []

        # Store the tkDGElement widgets in the data grid in a dictionary of lists.
        # Key is field name as string, value is list of tkDGElement objects for that field, as {string: [tkDGElement objects]}
        self._grid_elements = {}

        # Widget ID's for the widgets in the data grid.
        self._wids = []

        # Canvas row height and column width, in inches.
        self._row_h = 0.25 
        self._col_w = 1.0
        # Element separator line width, in inches.
        self._sep_w = 1./32.

        # Note: i=inches
        # Note: scrollregion=(w,n,e,s)
        # Determine how big the scroll region needs to be (in inches) to fit the specified number of records and fields,
        # plus the separator lines between the records and fields.
        scroll_height = f"{(self._num_records+1)*self._row_h + (self._num_records+2)*self._sep_w}i"
        num_fields = len(self._fields_config)
        scroll_width = f"{num_fields*self._col_w + (num_fields+1)*self._sep_w}i"
        self._dg_canvas = tk.Canvas(self, width='5i', height='4i',
                                    scrollregion=('0i','0i',scroll_width,scroll_height), background='gray75')
        self._dg_canvas.grid(column=0, row=0, sticky='NWSE') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        # Create a vertical Scrollbar and associate it with _txt_content
        self._scrollbar_vert = ttk.Scrollbar(self, command=self._dg_canvas.yview)
        self._scrollbar_vert.grid(column=1, row=0, sticky='NWSE')
        self._dg_canvas['yscrollcommand'] = self._scrollbar_vert.set

        # Create a horizontal Scrollbar and associate it with _txt_content
        self._scrollbar_hor = ttk.Scrollbar(self, command=self._dg_canvas.xview, orient='horizontal')
        self._scrollbar_hor.grid(column=0, row=1, sticky='NWSE')
        self._dg_canvas['xscrollcommand'] = self._scrollbar_hor.set

        # Bindings for mouse wheel scrolling on the canvas.
        # Reference: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        self._dg_canvas.bind('<Enter>', self._bound_to_mousewheel)
        self._dg_canvas.bind('<Leave>', self._unbound_to_mousewheel)

        # Store currently focused element widget, as tkDGElement object.
        self._focused_element = None

        # Set up the data grid with the appropriate number of records and fields.
        self._draw_element_separator_lines()
        self._setup_data_grid()

        # Create a dictionary to store figure templates for the data grid
        # key = name of figure (e.g., 'temperature vs depth'), as str
        # value = DataGridFigureTemplate child object
        self._fig_temps = {}

        # Create a tkDataGridFigureWidget
        self._figure = tkDataGridFigureWidget(self)
        self._figure.grid(column=0, row=0, columnspan=2, rowspan=2, sticky='NWSE', padx='0.1i', pady='0.1i') # Grid-2
        # Remove the figure widget from the grid, so that it is invisible, but so that it remembers its grid location.
        self._figure.grid_remove()
        # Restore the visibility of the data grid canvas and it's scroll bars (if needed?)
        self._dg_canvas.grid()
        self._scrollbar_hor.grid()
        self._scrollbar_vert.grid()

        # Process running the HelpApp
        self._help_process = None

    @property
    def num_records(self):
        return self._num_records

    @property
    def uomAdapter(self):
        return self._uom

    @property
    def canvas(self):
        return self._dg_canvas

    # ** Methods intended for client use **

    def register_figure_template(self, name, template):
        """
        Call this method to register a figure template for the data grid.
        :parameter name: The name of the figure, as string
        :parameter template: The DataGridFigureTemplate object for the figure, as DataGridFigureTemplate child object
        :return: None
        """
        assert(isinstance(name, str) and len(name)>0)
        assert(isinstance(template, DataGridFigureTemplate))
        self._fig_temps[name]=template
        return None

    def clear_grid_element_value(self, field_name='a_field_name', record_index=0):
        """
        Clear the value of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        Note: (1) A FieldType.TEXT element will have its value set to ''
              (2) A FieldType.BOOL element will have its value set to False
              (3) A FieldType.LIST element will have its value unchanged.
              (4) A FieldType.Number element will have its text value set to '' and its numeric value set to None.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            element.clear_element_value()
        return None

    def get_field_unit_group(self, field_name='a_field_name'):
        """
        Return the value of the unit of measurement group for a given field name. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :return: The value of the unit of measurement group for the given field name, or None if no such field name exists or the field has no associated unit group,
                 as any or None
        """
        assert(type(field_name)==str)
        field_header_element = [he for he in self._header_elements if he._raw_state==field_name]
        if len(field_header_element)>0:
            field_header_element = field_header_element[0]
        else:
            field_header_element = None
        if field_header_element is not None:
            return field_header_element._field_config.fieldUnitGroup
        else:
            return None

    def get_field_unitID(self, field_name='a_field_name'):
        """
        Return the value of the unit of measurement ID for a given field name. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :return: The value of the unit of measurement ID for the given field name, or None if no such field name exists or the field has no associated unit ID,
                 as any or None
        """
        assert(type(field_name)==str)
        field_header_element = [he for he in self._header_elements if he._raw_state==field_name]
        if len(field_header_element)>0:
            field_header_element = field_header_element[0]
        else:
            field_header_element = None
        if field_header_element is not None:
            return field_header_element._field_config.fieldUnitID
        else:
            return None

    def get_field_unit_name(self, field_name='a_field_name'):
        """
        Return the value of the unit of measurement name for a given field name. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :return: The value of the unit of measurement name for the given field name, or None if no such field name exists or '' if the field has no associated unit name,
                 as string or None
        """
        assert(type(field_name)==str)
        field_header_element = [he for he in self._header_elements if he._raw_state==field_name]
        if len(field_header_element)>0:
            field_header_element = field_header_element[0]
        else:
            field_header_element = None
        if field_header_element is not None:
            return field_header_element._field_config.fieldUnitName
        else:
            return None

    def get_grid_element_value(self, field_name='a_field_name', record_index=0):
        """
        Return the value of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: The value of the grid element for the given field name and record index, or None if no such element exists, as any or None
            Note: If the grid element is a FieldType.NUMBER, then the value returned will be the numeric value, not the text value,
                  and it will be in base units if the field has an associated unit group.
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            return element.get_state()[1]
        else:
            return None

    def get_grid_element_value_display_units(self, field_name='a_field_name', record_index=0):
        """
        Return the value of the grid element for a given field name and record index. If the element is a record for a
        field that has a unit group, then the value will be returned in the current display units. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: The value of the grid element for the given field name and record index, or None if no such element exists, as any or None
            Note: If the grid element is a FieldType.NUMBER, then the value returned will be the numeric value, not the text value,
                  and it will be in the current display units if the field has an associated unit group.
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            val_base_units = element.get_state()[1]
            if self._element_has_units(element):
                unit_grp = self.get_field_unit_group(field_name)
                base_unit_id = self.uomAdapter.get_base_unit_id_for_unit_group(unit_grp)
                disp_unit_id = self.get_field_unitID(field_name)
                val_disp_units = self.uomAdapter.convert(base_unit_id, disp_unit_id, val_base_units)
                return val_disp_units
            else:
                return val_base_units
        else:
            return None

    def get_grid_element_FieldType(self, field_name='a_field_name', record_index=0):
        """
        Return the FieldType of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: The FieldType of the grid element for the given field name and record index, or None if no such element exists, as FieldType or None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        # TODO: This is not OO. Improve. Maybe by having the tkDGElement classes return their FieldType when get_state() is called, or by having a method in tkDGElement that returns its FieldType.
        if element is not None:
            elem_type = element.get_state()[0]
            if elem_type == tkDGElementText:
                return FieldType.TEXT
            elif elem_type == tkDGElementBool:
                return FieldType.BOOL
            elif elem_type == tkDGElementList:
                return FieldType.LIST
            elif elem_type == tkDGElementNumber:
                return FieldType.NUMBER
            else:
                return None
        else:
            return None

    def get_grid_element_default_value(self, field_name='a_field_name', record_index=0):
        """
        Return the default value of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: The default value of the grid element for the given field name and record index, or None if no such element exists, as any or None
            Note: If the grid element is a FieldType.NUMBER, then the value returned will be the numeric value, not a text value,
                  and it will be in base units if the field has an associated unit group.
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            return element.get_default_value()
        else:
            return None

    def set_grid_element_value(self, field_name='a_field_name', record_index=0, value=None):
        """
        Set the value of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :parameter value: The value to set in the grid element, as any
            Note: If the grid element is a FieldType.NUMBER, then the value set should be the numeric value, not a text value,
                  and it should be in base units if the field has an associated unit group.
        :return: None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            element.set_state(value)
        return None

    def set_grid_element_default_value(self, field_name='a_field_name', record_index=0, value=None):
        """
        Set the default value of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :parameter value: The default value to set in the grid element, as any
            Note: If the grid element is a FieldType.NUMBER, then the value set should be the numeric value, not a text value,
                  and it should be in base units if the field has an associated unit group.
        :return: None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            element.set_default_value(value)
        return None

    def set_grid_element_list_choices(self, field_name='a_field_name', record_index=0, choices=tuple()):
        """
        Set the choices for a LIST grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :parameter choices: The choices to set for the LIST grid element, as tuple of strings
        :return: None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            if element.get_state()[0] == tkDGElementList:
                element.set_menu_choices(choices)
        return None

    def create_element_format(self, format_name = 'an_element_format', text_color = 'black', cell_color = 'white',
                              read_only = True, default_cell_color='#74BA00'):
        """
        Create a named configuration for formatting element widgets in the data grid.
        :parameter format_name: The name of the format, as string
        :parameter text_color: The color of the text in the element widget, as string
        :parameter cell_color: The background color of the element widget, as string
        :parameter read_only: If True, the element widget will not accept input, as boolean
        :parameter default_cell_color: The background color for the element widget if the value of the element
                                       is the default value for that element, as string
            Note: The default value for default_cell_color paramter is "Microsoft Green"
        :return None:
        """
        assert(type(format_name)==str)
        assert(type(text_color)==str)
        assert(type(cell_color)==str)
        assert(type(read_only)==bool)
        self._element_formats[format_name] = (text_color, cell_color, read_only, default_cell_color)
        return None

    # ** Methods NOT intended for client use **

    # * Mouse wheel scrolling methods for the data grid canvas *
    
    def _bound_to_mousewheel(self, event):
        """
        Called when data grid canvase is entered with the mouse pointer. Binds the mouse wheel to the canvas scroll.
        :parameter event: The tkinter event object for the event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget is binding to mouse wheel events.")
        self._dg_canvas.bind_all('<MouseWheel>', self._onMousewheel)
        return None

    def _unbound_to_mousewheel(self, event):
        """
        Called when data grid canvase is left by the mouse pointer. Unbinds the mouse wheel from the canvas scroll.
        :parameter event: The tkinter event object for the event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget is unbinding from mouse wheel events.")
        self._dg_canvas.unbind_all('MouseWheel>')
        return None

    def _onMousewheel(self, event):
        """
        Called when data grid recieves mouse scroll event. Scrolls the data grid canvas.
        :parameter event: The tkinter event object for the event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget received mouse wheel event for event delta of {event.delta}.")
        self._dg_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        return None

    # * Contextual menu methods for the data grid *

    def onContextMenu(self, event, element):
        """
        Handler for the <<ContextMenu>> virtual event. Display the contextual menu.
        :parameter event: The tkinter event object for the <<ContextMenu>> virtual event
        :parameter element: The tkDGElement object that Has the element widget that received the context menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget received <<ContextMenu>> virtual event from tkDGElement with canvas ID {element.canvasID}.")
        context_menu = self._create_context_menu(event, element)
        context_menu.post(event.x_root, event.y_root)
        return None

    # TODO:
    # Moved Copy, Paste, etc. to an Edit submenu if the context menu.
    # (1) For a writeable text element, Copy should get it's text value and put it on the clipboard, and Paste should get the text value from the clipboard and put it in the element widget, if the clipboard value is a string.
    #     If no text is selected, copy should get the entire text value of the element and put it on the clipboard. If text is selected, copy should get the selected text and put it on the clipboard. Paste should insert the clipboard text at the cursor position, or replace the selected text if there is a selection.
    # (2): For a read-only text element, Copy should get it's text value and put it on the clipboard, but Paste should do nothing.
    # (3): For a boolean element, Copy should get it's value and put it on the clipboard. Paste should only work it the clipboard value is a boolean, 0, or 1.
    # (4): For a list element, Copy should get it's value and put it on the clipboard. Paste should only work if the clipboard value is one of the options for the list element.
    # (5) Implication of all of this is probably that elements need to bind to the virtual events and have specific handling instead of the default handling.
    # If Paste should do nothing, it should be disabled.
    def _create_context_menu(self, event, element):
        """
        Create the contextual menu for the element widgets in the data grid.
        :parameter event: The tkinter event object for the <<ContextMenu>> virtual event
        :parameter element: The tkDGElement object that Has the element widget that received the context menu event, as tkDGElement object
        :return: The tkinter Menu widget that is the contextual menu, as tkinter Menu widget object
        """
        context_menu = tk.Menu(self)

        # Create "Delete" cascade menu
        delete_menu_obj=tk.Menu(context_menu)
        context_menu.add_cascade(menu=delete_menu_obj, label='Delete')
        # Create commands under "Delete"
        delete_menu_obj.add_command(label='Row', command=partial(self.onDeleteRowContextMenuOptionSelected, element))
        delete_menu_obj.add_command(label='Column', command=partial(self.onDeleteColumnContextMenuOptionSelected, element))

        # Create "Edit" cascade menu
        edit_menu_obj=tk.Menu(context_menu)
        context_menu.add_cascade(menu=edit_menu_obj, label='Edit')
        # Create commands under "Edit"
        edit_menu_obj.add_command(label='Copy', command=lambda: self._focused_element.elementWidget.event_generate('<<Copy>>'))
        edit_menu_obj.add_command(label='Paste', command=lambda: self._focused_element.elementWidget.event_generate('<<Paste>>'))

        # Create "Export" cascade menu
        xport_menu_obj=tk.Menu(context_menu)
        context_menu.add_cascade(menu=xport_menu_obj, label='Export')
        # Create commands under "Export"
        xport_menu_obj.add_command(label='PostScript', command=self.onExportPostscriptContextMenuOptionSelected)
        xport_menu_obj.add_command(label='CSV', command=self.onExportCSVContextMenuOptionSelected)
        xport_menu_obj.add_command(label='JSON', command=self.onExportJSONContextMenuOptionSelected)

        # Create "Help on Data Grid" command on context menu
        context_menu.add_command(label='Help on Data Grid', command=partial(self.onHelpOnDataGridContextMenuOptionSelected, element))

        # Create "Insert" cascade menu
        insert_menu_obj=tk.Menu(context_menu)
        context_menu.add_cascade(menu=insert_menu_obj, label='Insert')
        # Create commands under "Insert"
        insert_menu_obj.add_command(label='Row above', command=partial(self.onInsertRowContextMenuOptionSelected, 'above', element))
        insert_menu_obj.add_command(label='Row below', command=partial(self.onInsertRowContextMenuOptionSelected, 'below', element))
        insert_menu_obj.add_command(label='Column left', command=partial(self.onInsertColumnContextMenuOptionSelected, 'left', element))
        insert_menu_obj.add_command(label='Column right', command=partial(self.onInsertColumnContextMenuOptionSelected, 'right', element))

        # Create "Restore default value" command on context menu
        context_menu.add_command(label='Restore Default Value', command=partial(element.onKeyPressF3, event))

        # Create "Show graph" command on the context menu
        graph_menu_obj=tk.Menu(context_menu)
        context_menu.add_cascade(menu=graph_menu_obj, label='Show graph')
        # Create commands under "Show graph"
        for (fn, ft) in self._fig_temps.items():
            graph_menu_obj.add_command(label=fn, command=partial(self.onShowGraphContextMenuOptionSelected, fn, element))

        # Create "Unit change" command on context menu
        context_menu.add_command(label='Unit change', command=partial(self.onUnitChangeContextMenuOptionSelected, element))

        # Disable menu commands as required by specified user abilities or based on which element is selected in the grid
        elemement_is_header = isinstance(element, tkDGElementFieldHeader)
        # Handle disabling deletions of rows/columns as needed.
        if (self._fields_are_cols):
            if not self._user_abilities._can_delete_field:
                delete_menu_obj.entryconfigure('Column', state=tk.DISABLED)
            if not self._user_abilities._can_delete_record or elemement_is_header:
                delete_menu_obj.entryconfigure('Row', state=tk.DISABLED)
        else:
            if not self._user_abilities._can_delete_field:
                delete_menu_obj.entryconfigure('Row', state=tk.DISABLED)
            if not self._user_abilities._can_delete_record or elemement_is_header:
                delete_menu_obj.entryconfigure('Column', state=tk.DISABLED)
        # Disable Edit|Paste if element is read-only format
        if self._is_element_readonly(element):
            edit_menu_obj.entryconfigure('Paste', state=tk.DISABLED)
        # Handle disabling insertions of rows/columns as needed.
        if (self._fields_are_cols):
            if elemement_is_header:
                # Can't insert a new record above the field header
                insert_menu_obj.entryconfigure('Row above', state=tk.DISABLED)
            if not self._user_abilities._can_insert_field:
                insert_menu_obj.entryconfigure('Column left', state=tk.DISABLED)
                insert_menu_obj.entryconfigure('Column right', state=tk.DISABLED)
            if not self._user_abilities._can_insert_record:
                insert_menu_obj.entryconfigure('Row above', state=tk.DISABLED)
                insert_menu_obj.entryconfigure('Row below', state=tk.DISABLED)
        else:
            if elemement_is_header:
                # Can't insert a new record to the left of the field header
                insert_menu_obj.entryconfigure('Column left', state=tk.DISABLED)
            if not self._user_abilities._can_insert_field:
                insert_menu_obj.entryconfigure('Row above', state=tk.DISABLED)
                insert_menu_obj.entryconfigure('Row below', state=tk.DISABLED)
            if not self._user_abilities._can_insert_record:
                insert_menu_obj.entryconfigure('Column left', state=tk.DISABLED)
                insert_menu_obj.entryconfigure('Column right', state=tk.DISABLED)
        # Disable Restore default value if element has no default value or is for a read-only field.
        if element._element_widget['state']==tk.DISABLED or element._element_widget['state']=='readonly' or element._default_value is None:
            context_menu.entryconfigure('Restore Default Value', state=tk.DISABLED)
        # Disable Show graph if no figure templates have been registered
        if len(self._fig_temps) == 0:
            context_menu.entryconfigure('Show graph', state=tk.DISABLED)
        # Disable Unit change if element's field does not have units configured
        if not self._element_has_units(element):
            context_menu.entryconfigure('Unit change', state=tk.DISABLED)

        # For adding options that do not have a built-in event, use a partial to call a handler method in this tkDataGridWidget class, and pass in the option as an argument to the handler method.
        # TODO: Generalize by passing in a dictionary to the tkDataGridWidget constructor that defines labels and handlers.
        # This would be so that a client can add it's own specific contextual menu options.
        # for i in ('Client Placeholder 1', 'Client Placeholder 2'):
        #      context_menu.add_command(label=i, command=partial(self.onClientContextMenuOptionSelected, i))

        return context_menu

    def _figure_asks_show_grid(self):
        """
        Handler for when figure requests that grid be shown.
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Data grid figure has requested that data grid be shown.")
        self._figure.grid_remove()
        self._dg_canvas.grid()
        self._scrollbar_hor.grid()
        self._scrollbar_vert.grid()
        # TODO: Need to set focus back to the element from which the display of graph was requested, but
        # not entirely sure how to do this, since that element gets a focus out event after the graph is shown.
        #self._focused_element.focus_set()
        return None

    def onShowGraphContextMenuOptionSelected(self, which, element):
        """
        Handler called when Show graph is selected from the contextual menu.
        :parameter which: The graph to show, as string
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to show graph {which} for element with canvas ID {element.canvasID} was selected.")
        # Preserve the elment to which we want focus to return to when we exit the figure
        self._focused_element = element
        self._dg_canvas.grid_remove()
        self._scrollbar_hor.grid_remove()
        self._scrollbar_vert.grid_remove()
        self._figure.grid()
        # Get the figure template for the selected figure
        ft = self._fig_temps[which]
        self._figure.draw_figure(ft)
        self._figure.focus_figure_canvas()
        return None

    def onHelpOnDataGridContextMenuOptionSelected(self, element):
        """
        Handler called when Help on Data Grid is selected from the contextual menu.
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to get help on data grid for element with canvas ID {element.canvasID} was selected.")
        help_file_path = sysconfig.get_path('data') + '\\Help\\tkAppFramework\\DataGrid_HelpFile.md'
        if not self._help_process or not self._help_process.is_alive():
            # Help app is not running, so launch it
            
            # Get the help format by looking at the help file extension
            if help_file_path.endswith('md'):
                help_format='md'
            elif help_file_path.endswith('xhtml'):
                help_format='xhtml'
            else:
                help_format='txt'

            self._help_process = Process(target=_launch_help_app, name='HelpApp Process', kwargs={'help_file':help_file_path, 'help_format':help_format})
            self._help_process.start()
        return None

    def onUnitChangeContextMenuOptionSelected(self, element):
        """
        Handler called when Unit Change is selected from the contextual menu.
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to change units for grid element with canvas ID {element.canvasID} was selected.")
        (elem_field, elem_rec) = self._get_element_coords(element)
        field_config = [fc for fc in self._fields_config if fc.fieldName==elem_field][0]
        header_elem = [he for he in self._header_elements if he._raw_state==field_config.fieldName][0]
        header_elem.onDoubleClickBtn1(None)
        return None

    def onDeleteColumnContextMenuOptionSelected(self, element):
        """
        Handler called when Delete | Column is selected from the contextual menu.
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to delete column of grid element with canvas ID {element.canvasID} was selected.")
        # TODO: Implement column deletion, but ONLY when columns are records.
        return None

    def onDeleteRowContextMenuOptionSelected(self, element):
        """
        Handler called when Delete | Row is selected from the contextual menu. Only does a deletion if the
        row is a data grid record, and not if the row is a data grid field.
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to delete row of grid element with canvas ID {element.canvasID} was selected.")
        (field_name, record_index) = self._get_element_coords(element)
        assert(self._fields_are_cols)
        if self._fields_are_cols:
            # Rows are records, so delete a record
            if record_index is not None:
                # Element is NOT a field header element, so okay to delete its row
                self._deleteRecord(record_index)
                # Set focus to the element for the same field in the record...
                new_focus_element = None
                if self._num_records == 0:
                    # We've just deleted the last record, so then put the focus on the field header
                    new_focus_element = [he for he in self._header_elements if he._field_config.fieldName==field_name][0]
                elif record_index == 0:
                    # We've deleted what was the first record, so then put the  focus on what has become the new first record
                    new_focus_element = self._grid_elements[field_name][record_index]
                else:
                    # We've deleted a record that has a remaining record above it, so then put the focus on that record
                    new_focus_element = self._grid_elements[field_name][record_index-1]
                new_focus_element._element_widget.focus_set()
                self._focused_element = new_focus_element
        return None

    def _deleteRecord(self, index):
        """
        Utility function that deletes the index-th record.
        :parameter index: The record index of the recrod which will be deleted, as int
        :return: None
        """
        assert(self._fields_are_cols)
        # First, delete all of the element/cell separators/borders on the canvas
        self._dg_canvas.delete('tag_element_separator_line')
        if self._fields_are_cols:
            # Second, delete from the grid's canvas the elements that make up the index-th record.
            # Iterate through fields and remove from the canvas the element widgets for the index-th record.
            for (field_name, record_list) in self._grid_elements.items():
                element = record_list[index]
                self._dg_canvas.delete(element.canvasID)
            # Third, Move all record elements after index up a row
            # Calculate how far up, in -y-direction we need to move each element.
            # Note: This logic works IFF each row is the same height, which is expected to remain the case.
            y_add = -(self._row_h + self._sep_w)
            # Iterate through fields and records and make the moves.
            for (field_name, record_list) in self._grid_elements.items():
                for reci in range(index+1, len(record_list)):
                    self._dg_canvas.move(record_list[reci].canvasID, 0, f'{y_add}i')
            else:
                # Move all record elements after index over a column
                # Not currently implemented
                pass
            # Forth, remove elements for the deleted record from the field record lists.
            self._delete_record_elements(index)
            # Fifth, regenerate the element separator lines.
            self._draw_element_separator_lines()
            # Sixth, notify observers that a row has been deleted.
            self.notify([DataGridDeleteRecordUpdateHint(deleted_record_index=index)])
        return None

    def _delete_record_elements(self, index):
        """
        Utility function that deletes the elements for the index-th record from the data grid's list of records for each field.
        :parameter index: The record index at which the insertion should be done, as int
        :return: None
        """
        assert(self._fields_are_cols)
        for (field_name, record_list) in self._grid_elements.items():
            # Remove the record element from the list of record elements for the field
            removed_element = record_list.pop(index)
            # Remove the record element's widget's ID on the data grid's canvas from the list of canvas ID's maintained
            # by the data grid.
            self._wids.remove(removed_element.canvasID)
            # Detach the data grid as an observer of the record element
            removed_element.detach(self)
            # Destroy the element's widget.
            # If the element's widget is not destroyed, then it will continue to receive tkinter events, which
            # is problematic, in particular the entry change event.
            removed_element.elementWidget.destroy()
        # Decrement the number of records in the data grid
        self._num_records -= 1
        return None

    def onInsertRowContextMenuOptionSelected(self, where, element):
        """
        Handler called when Insert | Row above or Insert | Row below is selected from the contextual menu.
        :parameter where: Should the row be inserted 'above' or 'below', as string
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to insert row {where} grid element with canvas ID {element.canvasID} was selected.")
        (field_name, record_index) = self._get_element_coords(element)

        assert(self._fields_are_cols)
        if self._fields_are_cols:
            # Rows are records, so insert a record
            if where=='below':
                if record_index is None:
                    # Assume that element is a field header element
                    record_index = -1
                self._insertRecordAfter(record_index)
            elif where=='above':
                if record_index is not None:
                    # Only allow insert 'above' if element is NOT a header element
                    self._insertRecordAfter(record_index-1)
        else:
            # Rows are fields, so insert a field
            # Not currently implemented
            pass
        return None

    def _insertRecordAfter(self, index):
        """
        Utility function that inserts a new record after the index-th record. If index = -1, then the newly iserted
        record will become the first record.
        :parameter index: The record index after which the insertion should be done, as int
        :return: None
        """
        assert(self._fields_are_cols)
        # First, delete all of the element/cell separators/borders on the canvas
        self._dg_canvas.delete('tag_element_separator_line')
        # Second, move all record elements after index down a row, or over a column.
        if self._fields_are_cols:
            # Move all record elements after index down a row
            # Calculate how far down, in +y-direction we need to move each element.
            # Note: This logic works IFF each row is the same height, which is expected to remain the case.
            y_add = self._row_h + self._sep_w
            # Iterate through fields and records and make the moves.
            for (field_name, record_list) in self._grid_elements.items():
                for reci in range(index+1, len(record_list)):
                    self._dg_canvas.move(record_list[reci].canvasID, 0, f'{y_add}i')
        else:
            # Move all record elements after index over a column
            # Not currently implemented
            pass
        # Third, create elements for the new record and insert them into the field record lists.
        self._create_new_record(index+1)
        # Fourth, regenerate the element separator lines.
        self._draw_element_separator_lines()
        # Fifth, notify observers that a row has been added.
        self.notify([DataGridAddRecordUpdateHint(new_record_index=index+1)])
        return None

    def _create_new_record(self, index):
        """
        Utility function that creates the elements for a new record at the index-th record. If index = -1, then the new
        elements will be become the first record.
        :parameter index: The record index at which the insertion should be done, as int
        :return: None
        """
        assert(self._fields_are_cols)
        # Widget height and width, in inches
        wid_h = self._row_h 
        wid_w = self._col_w
        # Add record widgets...
        new_focus_element = None
        field_index = 0
        for field in self._fields_config:
            if self._fields_are_cols:
                next_x = (field_index * wid_w) + ((field_index + 1) * self._sep_w)
                next_y = ((index + 1) * wid_h) + ((index + 2) * self._sep_w)
            else:
                # Not currently implemented
                pass
            field_name = field.fieldName
            field_type = field.fieldType
            field_format = field.fieldFormat
            # TODO: Well, this is ugly, non-OO code...
            element = None
            match field_type:
                case FieldType.BOOL:
                    element = tkDGElementBool(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                case FieldType.LIST:
                    element = tkDGElementList(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                case FieldType.TEXT:
                    element = tkDGElementText(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                case FieldType.NUMBER:
                    element = tkDGElementNumber(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
            # Tag the element's canvas ID with the field name, so we can "address" all of a field's elements as a group.
            # TODO: This may turn out to not actually be useful/needed.
            self._dg_canvas.addtag_withtag(f"tag_{field_name}", element.canvasID)
            if new_focus_element is None:
                new_focus_element = element
            self.register_subject(element, partial(self.handle_element_update, element))
            self._wids.append(element.canvasID)
            # Store the list of tkDGElement objects for this field in the _grid_elements dictionary.
            self._grid_elements[field_name].insert(index, element)
            # Configure the element's widget with the appropriate format.
            self._apply_element_format_to_one_element(field_format, element)
            # Advance field_index for next iteration of field loop.
            field_index += 1
        # Set focus to the 0-th field_index element for the new record
        if new_focus_element is not None:
            new_focus_element._element_widget.focus_set()
            self._focused_element = new_focus_element
        # Increment the number of records for the grid
        # TODO: Consider refactoring such that the number of records is determined from the length of the lists
        # in the grid element dictionary, so that there can't be an inconsistency.
        self._num_records += 1
        return None

    def onInsertColumnContextMenuOptionSelected(self, where, element):
        """
        Handler called when Insert | Column left or Insert | Column right is selected from the contextual menu.
        :parameter where: Should the column be inserted to the left or right
        :parameter element: The tkDGElement object that Has the element widget that received the contextual menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option to insert column to the {where} of grid element with canvas ID {element.canvasID} was selected.")
        # TODO: Implement column insertion
        return None

    def onExportPostscriptContextMenuOptionSelected(self):
        """
        Handler called when Export|Postscript is selected from the contextual menu.
        :return: None
        """
        initial_dir = getcwd()
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(defaultextension='eps', filetypes=[('Encapsulated PostScript file', '*.eps')],
                                                initialdir=initial_dir, title='Select file to write PostScript to')
        if len(response)>0: # User did not cancel
            # TODO: Use height and width parameters to generate postscript for entire canvas, not just the
            # visible area.
            self._dg_canvas.postscript(colormode='color', file=response)
        return None

    def onExportCSVContextMenuOptionSelected(self):
        """
        Handler called when Export|CSV is selected from the contextual menu.
        :return: None
        """
        initial_dir = getcwd()
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(defaultextension='csv', filetypes=[('Comma Separated Values file', '*.csv')],
                                                initialdir=initial_dir, title='Select file to write CSV to')
        if len(response)>0: # User did not cancel
            # TODO: Convert the data grid to csv and write to the selected file
            pass
        return None

    def onExportJSONContextMenuOptionSelected(self):
        """
        Handler called when Export|JSON is selected from the contextual menu.
        :return: None
        """
        initial_dir = getcwd()
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(defaultextension='json', filetypes=[('Java Script Object Notation file', '*.json')],
                                                initialdir=initial_dir, title='Select file to write JSON to')
        if len(response)>0: # User did not cancel
            # TODO: Convert the data grid to JSON and write to the selected file
            pass
        return None

    def onClientContextMenuOptionSelected(self, option):
        """
        Handler for when an option is selected from the contextual menu.
        :parameter option: The option that was selected, as string
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option {option} was selected.")
        return None

    # * Focus and keyboard event handlers for the data grid *
    # Note: These are intended to be called from the tkDGElement objects that are the element widgets in the data grid.

    def onFocusIn(self, element):
        """
        Handler for the FocusIn events. Update it's tracking of currently focused element to the event's widget.
        Note: Intended to be called from tkDGElement.onFocusIn(...).
        :parameter element: The tkDGElement object that Has the element widget that received focus, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget received FocusIn event from tkDGElement with canvas ID {element.canvasID}.")
        
        self._focused_element = element
        self._draw_focus_rectangle(element)
        return None

    def onFocusOut(self, element):
        """
        Handler for the FocusOut event. Update it's tracking of currently focused element to None.
        :parameter element: The tkDGElement object that Has the element widget that lost focus, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget received FocusOut event from tkDGElement with canvas ID {element.canvasID}.")
        self._focused_element = None
        return None

    def onKeyPressUp(self, event):
        """
        Handler for the up-arrow key press event. Moves focus to the element widget above the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget received KeyPress-Up event.")
        if self._focused_element is not None:
            logger.debug(f"     focused element has canvas ID {self._focused_element.canvasID}.")
            (field_name, record_index) = self._get_element_coords(self._focused_element)
            next_element = None
            if record_index > 0:
                next_element = self._get_grid_element(field_name, record_index - 1)
            elif record_index == 0:
                # If the focused element is in the first record, then move focus to the field header element for the same field.
                next_element = [elem for elem in self._header_elements if elem._raw_state == field_name][0]
            if next_element is not None:
                self._ensure_element_widget_visible(next_element)
                next_element._element_widget.focus_set()
                self._focused_element = next_element
        return None

    def _ensure_element_widget_visible(self, element):
        """
        Scroll the canvas as needed to ensure that element parameter's widget is in the canvas's currently visible area.
        :parameter element: The tkDGElement object that Has the element widget that needs to be made visible, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        
        # Make sure that the paramter element is visible on the canvas.
        
        # Get the bounding box of the element's widget on the canvas, in canvas coordinates
        (etlx, etly, ebrx, ebry) = self._dg_canvas.bbox(element.canvasID)
        logger.debug(f"     Element bounds: ({etlx},{etly}), ({ebrx},{ebry}).")
        # Get the bounding box of the entire canvas, in canvas coordinates
        (ctlx, ctly, cbrx, cbry) = self._dg_canvas.bbox('all')
        logger.debug(f"     Canvas bounds: ({ctlx},{ctly}), ({cbrx},{cbry}).")
        # Get the bounding box of the currently visible area of the canvas, in canvas coordinates
        vtlx = self._dg_canvas.canvasx(0)
        vtly = self._dg_canvas.canvasy(0)
        vbrx = self._dg_canvas.canvasx(self._dg_canvas.winfo_width())
        vbry = self._dg_canvas.canvasy(self._dg_canvas.winfo_height())
        logger.debug(f"     Canvas visible area bounds: ({vtlx},{vtly}), ({vbrx},{vbry}).")
        
        # TODO: Scrolling is a little odd when going down or right, because it scrolls so the element is at the top
        # or left of the visible area (or not exactly if the scroll bar runs out of room). Probably a user expects
        # just enough scroll to bring the element into view, not necessarily to the top or left of the visible area.
        # Improved logic for scrolling may depend on if we are moving up/down or left/right?
        
        # Check if the element's widget is horizontally out of the visible area of the canvas
        if (etlx < vtlx) or (ebrx > vbrx):
            # Scroll the canvas horizontally to bring the element's widget into view
            logger.debug(f"     Horizontal scroll fraction: {(etlx-ctlx) / (cbrx-ctlx)}.")
            self._dg_canvas.xview_moveto((etlx-ctlx) / (cbrx-ctlx))
        # Check if the element's widget is vertically out of the visible area of the canvas
        if (etly < vtly) or (ebry > vbry):
            # Scroll the canvas vertically to bring the element's widget into view
            logger.debug(f"     Vertical scroll fraction: {(etly-ctly) / (cbry-ctly)}.")
            self._dg_canvas.yview_moveto((etly-ctly) / (cbry-ctly))

        return None

    def onKeyPressDown(self, event):
        """
        Handler for the down-arrow key press event. Moves focus to the element widget below the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        if self._focused_element is not None:
            (field_name, record_index) = self._get_element_coords(self._focused_element)
            if record_index < self._num_records - 1:
                next_element = self._get_grid_element(field_name, record_index + 1)
                if next_element is not None:
                    self._ensure_element_widget_visible(next_element)
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
        return None

    def onKeyPressRight(self, event):
        """
        Handler for the right-arrow key press event. Moves focus to the element widget to the right of the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        if self._focused_element is not None:
            (field_name, record_index) = self._get_element_coords(self._focused_element)
            field_config = [fc for fc in self._fields_config if fc.fieldName==field_name]
            field_index = self._fields_config.index(field_config[0])
            if field_index < len(self._fields_config) - 1:
                next_element = self._get_grid_element(self._fields_config[field_index+1].fieldName, record_index)
                if next_element is not None:
                    self._ensure_element_widget_visible(next_element)
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
        return None

    def onKeyPressLeft(self, event):
        """
        Handler for the Left-arrow key press event. Moves focus to the element widget to the left of the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        if self._focused_element is not None:
            (field_name, record_index) = self._get_element_coords(self._focused_element)
            field_config = [fc for fc in self._fields_config if fc.fieldName==field_name]
            field_index = self._fields_config.index(field_config[0])
            if field_index > 0:
                next_element = self._get_grid_element(self._fields_config[field_index-1].fieldName, record_index)
                if next_element is not None:
                    self._ensure_element_widget_visible(next_element)
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
        return None

    # * Utility functions for the data grid *

    def _is_element_readonly(self, element):
        """
        Utility function for determinig if a data grid element is readonly.
        :parameter element: The tkDGElement object for which to determine readonly status, as tkDGElement object
        :return: True if data grid element is readonly, otherwise False, as boolean
        """
        assert(isinstance(element, tkDGElement))
        # Get the field of the parameter element
        (field_name, rec_index) = self._get_element_coords(element)
        # Get the field configuration for the element's field, using list comprehension
        field_config = [fc for fc in self._fields_config if fc.fieldName==field_name][0]
        field_format = field_config.fieldFormat
        isReadonly = self._element_formats[field_format][2]
        return isReadonly

    def _element_has_units(self, element):
        """
        Utility function for determine if a data grid element's field has units of measure.
        :parameter element: The tkDGElement object for which to determine units of measure status, as tkDGElement object
        :return: True if data grid element's field has units of measure, otherwise False, as boolean
        """
        assert(isinstance(element, tkDGElement))
        # Get the field of the parameter element
        (field_name, rec_index) = self._get_element_coords(element)
        # Get the field configuration for the element's field, using list comprehension
        field_config = [fc for fc in self._fields_config if fc.fieldName==field_name][0]
        if field_config.fieldUnitGroup is not None:
            return True
        else:
            return False
    
    def _get_grid_element(self, field_name='a_field_name', record_index=0):
        """
        Return the tkDGElement object for a given field name and record index.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
            Note: If the record_index is -1, then the field header element for the given field name will be returned.
        :return: The tkDGElement object for the given field name and record index, or None if no such element exists, as tkDGElement object or None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = None
        if record_index == -1:
            elem_list = [elem for elem in self._header_elements if elem._raw_state==field_name]
            if len(elem_list)>0:
                element = elem_list[0]
        elif field_name in self._grid_elements:
            if record_index < len(self._grid_elements[field_name]):
                element = self._grid_elements[field_name][record_index]
        return element
    
    def _get_element_coords(self, element=None):
        """
        Return the field name and record index for a given tkDGElement object.
        :parameter element: The tkDGElement object for which to find the field name and record index, as tkDGElement object
        :return: Tuple (field name, 0-based record index), as (string, int)
            Note: If the element is a field header element, then the record index will be -1.
        """
        assert(isinstance(element, tkDGElement))
        if isinstance(element, tkDGElementFieldHeader):
            return (element._raw_state, -1)
        else: # NOT a field header element, but a record element
            for field_name in self._grid_elements:
                if element in self._grid_elements[field_name]:
                    record_index = self._grid_elements[field_name].index(element)
                    break
        return (field_name, record_index)

    def _apply_element_format_to_one_element(self, elem_format='a_field_header', element=None):
        """
        Apply a named element format to one element widget.
        :parameter elem_format: The name of the format to apply, as string
        :parameter element: The tkDGElement object whose element widget the format will be applied to, as tkDGElement object
        """
        assert(type(elem_format)==str)
        assert(isinstance(element, tkDGElement))
        if elem_format in self._element_formats:
            text_color, cell_color, read_only, default_cell_color = self._element_formats[elem_format]
            element._element_widget.configure(background=cell_color, highlightcolor=cell_color, foreground=text_color)
            # TODO: Fix this horribly non-OO code.
            if element.get_state()[0] == tkDGElementFieldHeader:
                element._element_widget.configure(font=font.nametofont('TkHeadingFont'))
            if element.get_state()[0] == tkDGElementText or element.get_state()[0] == tkDGElementNumber:
                element.elementWidget.configure(readonlybackground=cell_color)
            element.disable_element(read_only)
        return None

    def _apply_element_format_to_field_elements(self, format_name = 'an_element_format', field_name = 'a_field_name'):
        """
        Apply a named element format to all the element widgets for a field.
        :parameter format_name: The name of the format to apply, as string
        :parameter field_name: The name of the field whose element widgets the format will be applied to, as string
        :return None:
        """
        assert(type(format_name)==str)
        assert(type(field_name)==str)
        if format_name in self._element_formats:
            if field_name in self._grid_elements:
                for element in self._grid_elements[field_name]:
                    self._apply_element_format_to_one_element(format_name, element)
        return None

    # TODO: Consider if this method should be moved to ObserverPatternBase.Observer class, since it has now been
    # implemented in both tkDataGridWidget and tkViewManager. This will require careful thinking, since an Observer
    # need not be a tkinter widget.
    def onDestroy(self, event):
        """
        Method called after ttk.LabelFrame is destroyed.
        :return: None
        """
        # Detach this observer from it's subjects, the child widgets (tkDGElement objects) of the data grid
        self._detach_from_subjects()
        return None

    def handle_element_update(self, element=None, hints=None):
        """
        Handler function called when a tkDGElement object notifies the tkDataGridWidget of a change in state.
        parameter element: The tkDGElement object that is notifying the tkDataGridWidget of a change in state, as tkDGElement object
        :parameter hints: An optional lisg of hints provided by element to specify what types of 
                          updates has occurred and details about them, as [ObserverPatterBase.UpdateHint object]
        :return None:
        """
        assert(isinstance(element, tkDGElement))
        
        logger = logging.getLogger('tkDataGridWidget_logger')
        (elem_field, elem_rec) = self._get_element_coords(element)
        value = element.get_state()[1] # This will be in base units if element is a number element associated with a field with a unitID
        default_value = element.get_default_value() # Also in base units if element is a number element associated with a field with a unitID
        logger.debug(f"tkDataGridWidget received update from tkDGElement with canvas ID {element.canvasID}. Elements state is {value}. Elemeht has default value {default_value}")

        if hints is not None and isinstance(hints, list):
            for hint in hints:
                assert(isinstance(hint, UpdateHint))
        
                if isinstance(hint, FieldHeaderElementTextUpdateHint):
                    # The raw state, i.e., the name of the field header has changed.
                    # Look up the field configuration using the previous name.
                    prev_field_name = hint.prev_raw_state
                    if len(prev_field_name)>0: # So we skip the first state setting upon grid setup.
                        elem_config = [fc for fc in self._fields_config if fc.fieldName==prev_field_name][0]
                        # Update the field configuration with the new field name.
                        elem_config._field_name = element._raw_state

                # Handle units of measure changes
                if isinstance(hint, FieldHeaderElementUnitsUpdateHint):
                    # The hint tells us what unit change has occurred
                    # Iterate through the field's records and and call set_state() on each record element,
                    # passing in the value in base units. set_state() will convert the value to the new units and update the element widget.
                    elem_config = [fc for fc in self._fields_config if fc.fieldName==elem_field][0]
                    # TODO: and clause of if below is NOT OO. Try to improve.
                    if element._raw_state in self._grid_elements and (elem_config.fieldType != FieldType.BOOL):
                        for rec_element in self._grid_elements[element._raw_state]:
                            val = rec_element.get_state()[1] # This is in base units
                            rec_element.set_state(val)

                # Handle formating the element widget appropriately based on if it has the default value or not.
                if isinstance(hint, RecordElementValueUpdateHint) or isinstance(hint, RecordElementDefaultValueUpdateHint):
                    elem_config = [fc for fc in self._fields_config if fc.fieldName==elem_field][0]
                    if default_value is not None:
                        elem_format = self._element_formats[elem_config.fieldFormat]
                        if value is not None:
                            if isinstance(value, float) or isinstance(value, int):
                                # TODO: Not very OO to indirectly infer element type.
                                # Handling tkDGElementNumber elements
                                if isclose(value, default_value, rel_tol=1e-7):
                                    element._element_widget.configure(background=elem_format[3])
                                else:
                                    element._element_widget.configure(background=elem_format[1])
                            else:
                                # Handling other element types
                                if value == default_value:
                                    element._element_widget.configure(background=elem_format[3])
                                else:
                                    element._element_widget.configure(background=elem_format[1])
                        else:
                            # value is None and default_value is not None, so background should NOT be the default color
                            element._element_widget.configure(background=elem_format[1])
                            
                # Create a hint for notifying the client of the data grid widget that a particular field of a particular record has changed value. 
                if isinstance(hint, RecordElementValueUpdateHint):
                    client_hint = DataGridChangedRecordUpdateHint(changed_record_field=elem_field, changed_record_index=elem_rec)
                    self.notify([client_hint])
        return None
        
    # TODO: Due to rounding, leaves behind a narrow red "shadow". Think about how to address this.
    def _draw_focus_rectangle(self, element):
        """
        Draw a rectangle around the element widget that has focus.
        :parameter element: The tkDGElement object that has focus, as tkDGElement object
        :return: None
        """
        assert(isinstance(element, tkDGElement))
        # Remove any existing focus rectangle. (Okay if the tagged rectangle doesn't exist.)
        self._dg_canvas.delete('tag_focus_rectangle')
        # Get the root window to get the DPI for converting inches to pixels.
        root = self.winfo_toplevel()
        dpi = root.winfo_fpixels('1i')
        # Get the coordinates of the element widget on the canvas, which should be in pixels.
        coords = self._dg_canvas.coords(element.canvasID)
        # Calculate the coordinates of the rectangle to draw around the element widget, in pixels.
        x0 = coords[0] - self._sep_w * dpi
        y0 = coords[1] - self._sep_w * dpi
        x1 = x0 + (self._col_w + self._sep_w) * dpi
        y1 = y0 + (self._row_h + self._sep_w) * dpi
        # Draw a rectangle around the element widget.
        self._dg_canvas.create_rectangle(x0, y0, x1, y1, outline='red', width=f'{self._sep_w}i',
                                         tags='tag_focus_rectangle')
        return None
    
    # TODO: Enhance so that fields can be columns instead of rows.
    def _draw_element_separator_lines(self):
        """
        This utility function is used to draw the lines on the canvas which visuall separate the elements
        into a grid.
        :return: None
        """
        # Note: start_x, start_y, end_x, end_y are coordinates (canvas?) where lines should start and end, in inches
        # First, draw vertical lines to separate fields/columns.
        start_y = 0.0
        # Remember that we need to account for the field header row, hence the +1's and +2's below.
        end_y = ((self._num_records+1) * self._row_h) + ((self._num_records+2)*self._sep_w)
        for field_i in range(len(self._fields_config) + 1):
                start_y = 0.0
                start_x = (field_i * self._col_w) + (field_i * self._sep_w)
                self._dg_canvas.create_line(f"{start_x}i", f"{start_y}i", f"{start_x}i", f"{end_y}i",
                                            width=f"{self._sep_w}i", tags='tag_element_separator_line')
        # Second, draw horizontal lines to separate records/rows.
        end_x = (len(self._fields_config) * self._col_w) + ((len(self._fields_config) +1)*self._sep_w)
        start_x = 0.0
        for rec_i in range(self._num_records + 2):
                start_y = (rec_i * self._row_h) + (rec_i * self._sep_w)
                self._dg_canvas.create_line(f"{start_x}i", f"{start_y}i", f"{end_x}i", f"{start_y}i",
                                            width=f"{self._sep_w}i", tags='tag_element_separator_line')

        return None
    
    # TODO: Enhance so that fields can be columns instead of rows.
    def _setup_data_grid(self):
        """
        Set up the data grid with the appropriate array of tkDGElement widgets for the fields and records.
        :return: None
        """
        # Note: next_x, next_y are coordinates (canvas?) where next widget should be inserted, in inches
        # Must set width and height for all widgets, so that these coordinates can be appropriately calculated.
        # Widget height and width, in inches
        wid_h = self._row_h 
        wid_w = self._col_w
        # Add widgets...
        upper_left_element = None
        field_index = 0
        for field in self._fields_config:
            next_x = (field_index * wid_w) + ((field_index + 1) * self._sep_w)
            field_name = field.fieldName
            field_type = field.fieldType
            field_format = field.fieldFormat
            field_unit_grp = field.fieldUnitGroup
            # Handle the field header element for this field/column.
            element = tkDGElementFieldHeader(self, x=next_x, y=self._sep_w, w=wid_w, h=wid_h, field_config=field)
            self.register_subject(element, partial(self.handle_element_update, element))
            self._wids.append(element.canvasID)
            if field_unit_grp is not None:
                uids = self._uom.get_unit_ids_of_unit_group(field_unit_grp)
                unames = self._uom.get_unit_names_for_unit(uids[0])
                element.set_state(field_name)
                element.set_units(field_unit_grp, uids[0], unames[0])
            else:
                element.set_state(field_name)
            self._apply_element_format_to_one_element('field_header', element)
            self._header_elements.append(element)
            # End handling the field header element for this field/column.
            rec_list = []
            for rec_i in range(self._num_records):
                next_y = ((rec_i + 1) * wid_h) + ((rec_i + 2) * self._sep_w)
                # TODO: Well, this is ugly, non-OO code...
                element = None
                match field_type:
                    case FieldType.BOOL:
                        element = tkDGElementBool(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.LIST:
                        element = tkDGElementList(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.TEXT:
                        element = tkDGElementText(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.NUMBER:
                        element = tkDGElementNumber(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                # Tag the element's canvas ID with the field name, so we can "adress" all of a field's elements as a group.
                # TODO: This may turn out to not actually be useful/needed.
                self._dg_canvas.addtag_withtag(f"tag_{field_name}", element.canvasID)
                if upper_left_element is None:
                    upper_left_element = element
                self.register_subject(element, partial(self.handle_element_update, element))
                self._wids.append(element.canvasID)
                rec_list.append(element)
            # Store the list of tkDGElement objects for this field in the _grid_elements dictionary.
            self._grid_elements[field_name] = rec_list
            # Configure the field's element widgets with the appropriate format.
            self._apply_element_format_to_field_elements(field_format, field_name)
            # Advance field_index for next iteration of field loop.
            field_index += 1
        
        # Set focus to upper left widget in data grid, if it exists.
        if upper_left_element is not None:
            upper_left_element._element_widget.focus_set()
            self._focused_element = upper_left_element

        return None

    def _setup_logging(self, log_level=logging.INFO):
        """
        This method configures logging.
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        :return: None
        """
        # Create a logger with name 'tkDataGridWidget_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('tkDataGridWidget_logger')
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
