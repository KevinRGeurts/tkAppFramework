"""
This module defines the tkDataGridWidget class. It is a tkinter widget that uses a tkinter Canvas widget to display
data records and fields.

Exported Classes:
    tkDataGridWidget -- It is a tkinter widget that uses a tkinter Canvas widget to display
                        data records and fields. It is a Subject in an Observer design pattern,
                        in anticipation of being observed by a tkViewManager.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
from dataclasses import field
import logging
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter.messagebox import showerror
from functools import partial
from enum import IntEnum
from xml.sax.handler import property_declaration_handler

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer, UpdateHint
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError
from tkAppFramework.uomsysadapter import UoMSysAdapter
from tkAppFramework.tkdgw_unitselect_dlg import tkUnitSelectDlg


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
        :parameter unit_group: The current unit ID for the field, or None if not applicable, as Any|None
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

    def clear_element_value(self):
        """
        Clear the element value. Must be implemented by child classes, since the way to clear the value will depend on the type of element.
        Note: Must be extended by child classes, because this base class implementation does nothing with the element's value.
              It does, however, call self.notify(), so when extending, call the base class implementation at the end of the extended method.
        :return: None
        """
        self.notify()
        return None

    def set_default_value(self, def_value):
        """
        Set the default value for the element, which is used to reset the element to a default state when needed.
        :parameter def_value: The default value for the element, as any (or None, if the element has no default value).)
        :return: None
        """
        self._default_value = def_value
        self.notify()
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
            self._element_widget.bind('<KeyPress-Delete>', self.onKeyPressDelete, add='+')
            self._element_widget.bind('<<ContextMenu>>', self.onContextMenu, add='+')
        return None

    def onKeyPressDelete(self, event):
        """
        Handler for the delete key press event. Delete key will restore the element's value to it's default, if
        one exists, set a BOOL element to False, or set a TEXT element to an emtpy string.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        # If the element is for a field that is read-only format, do nothing.
        if self._element_widget['state']!=tk.DISABLED and self._element_widget['state']!='readonly':
            if self._default_value is not None:
                self._element_value.set(self._default_value)
            else:
                self.clear_element_value()
            self.notify()
        return None

    def onContextMenu(self, event):
        """
        Handler for the <<ContextMenu>> virtual event. Call handler in element widget's grandparent tkDataGridWidget to
        handle the contextual menu.
        :parameter event: The tkinter event object for the <<ContextMenu>> virtual event
        :parameter element: The tkDGElement object that Has the element widget that received the context menu event, as tkDGElement object
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
        self.notify()
        return None

    def set_state(self, value=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element.
        Note: Must be extended by child classes, because this base class implementation does nothing with value parameter.
              It does, however, call self.notify(), so when extending, call the base class implementation at the end of the extended method.
        :return: None
        """
        assert(type(value)==bool)
        self._element_value.set(int(value))
        super().set_state()
        return None

    def clear_element_value(self):
        """
        Clear the element value, by setting it to False.
        :return: None
        """
        self.set_state(False)
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
        self._element_value.set(option)
        self._element_widget.focus_set()
        self.notify()
        return None

    def set_state(self, value=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element.
=        :return: None
        """
        assert(type(value)==str)
        # TODO: Check that value is in the list of options for the OptionMenu.
        self._element_value.set(value)
        super().set_state()
        return None

    def clear_element_value(self):
        """
        Clear the element value. Actually this does nothing, since there is no clear value for an OptionMenu, but method must be implemented since it is abstract in the base class.
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
        if len(field_config) > 0:
            field_config = field_config[0]
            validator = field_config.fieldValidator
            if validator is not None:
                try:
                    validator(proposed_entry = self._element_value.get())
                except tkDGElementTextInvalidEntryError as e:
                    showerror(title='Data Grid Text Entry Error', message=e.args[0], parent=self._element_widget.master)
                    return False
        # Inform all observers of the change in the text entry
        try:
            # Validity here is still only an assumption. Observer(s) could raise exception if they have
            # a problem with the new entry value when notify() is called, and OnInvalidEntryChange() will correct to False.
            self.notify()
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

    def set_state(self, value=None):
        """
        Set the state of the text element.
        :paramter value: The value to set in the element.
        :return: None
        """
        assert(type(value)==str)
        old_value = self._element_value.get()
        # Only set the value and notify observers if the value has actually changed, to avoid unnecessary updates.
        if value != old_value:
            self._element_value.set(value)
            super().set_state()
        return None

    def clear_element_value(self):
        """
        Clear the element value, by setting it to ''.
        :return: None
        """
        self.set_state('')
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

    def clear_element_value(self):
        """
        Clear the element value, by setting it to ''.
        :return: None
        """
        self.set_state('')
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


    def OnEntryChanged(self, canvas_id):
        """
        Event handler for changes to Number entry.
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
            if (_proposed_entry is not None) and (len(_proposed_entry)>0):
                self.set_state(float(_proposed_entry))
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
        self.notify()
        return None

    def set_state(self, value=None):
        """
        Set the state of the number element.
        :paramter value: The numeric value to set in the element, as float|int|None
        :return: None
        """
        assert((value is None) or (type(value)==float) or (type(value)==int))
        old_value = self._numeric_value
        # Only set the value and notify observers if the value has actually changed, to avoid unnecessary updates.
        if value != old_value:
            self._numeric_value = value
            if value is None:
                self._element_value.set('')
            else:
                self._element_value.set(self._format_value(value))
            self.notify()
        return None

    def _format_value(self, value):
        """
        This utility function applies logic to format a float or int value as a string, so that scientific notation is
        used if the number is particularly small or large.
        """
        assert(isinstance(value, int) or isinstance(value, float))
        formatted_value = '{:.8G}'.format(value)
        return formatted_value

    def clear_element_value(self):
        """
        Clear the element value, by setting it to None.
        :return: None
        """
        self.set_state(None)
        # DON"T call super().clear_element_value(), as set_state() already calls notify().
        return None

    def get_state(self):
        """
        Get the state of the number element.
        :return: Tuple (element type, element value), as (type, int|float|None)
        """
        value = self._numeric_value
        return (type(self), value)


class tkDataGridWidget(Subject, Observer, ttk.Labelframe):
    """
    Class represents a tkinter label frame, the widget contents of which allow displayinbg and interacting with
    data records and fields. Class is a Subject in Observer design pattern so that it can be observed by a tkViewManager object.
    Class is an Observer in Observer design pattern so that it can observe tkDGElement objects.
    """
    # TODO: Pass in row heights and collumn widths?
    def __init__(self, parent, title='Data Grid', fields_config=[], num_records=0, log_level = logging.INFO, uom_adapter = None) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter title: The text label of the Labelframe, as string
        :parameter fields_config: List of FieldConfiguraton objects specifying the configuration of each field in the data grid,
                                  as [FieldConfiguration object]
        :parameter num_records: The number of records to display in the data grid, as int
        :parameter log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        :parameter uom_adapter: The Units of Measure System Adapter to be used by the data grid, as UoMSysAdapter object or None
        """
        Subject.__init__(self)
        Observer.__init__(self)
        ttk.Labelframe.__init__(self, parent, text=title)

        # Set up logging for this class.
        self._setup_logging(log_level)

        if uom_adapter is not None:
            assert(isinstance(uom_adapter, UoMSysAdapter))
        self._uom = uom_adapter

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

        # Store currently focused element widget, as tkDGElement object.
        self._focused_element = None
        # Store most recently modified element widget, as tkDGElement object.
        self._modified_element = None

        # Set up the data grid with the appropriate number of records and fields.
        self._draw_element_separator_lines()
        self._setup_data_grid()

    @property
    def num_records(self):
        return self._num_records

    @property
    def modifiedElement(self):
        return self._modified_element

    @property
    def uomAdapter(self):
        return self._uom

    def onContextMenu(self, event, element):
        """
        Handler for the <<ContextMenu>> virtual event. Display handle the contextual menu.
        :parameter event: The tkinter event object for the <<ContextMenu>> virtual event
        :parameter element: The tkDGElement object that Has the element widget that received the context menu event, as tkDGElement object
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"tkDataGridWidget received <<ContextMenu>> virtual event from tkDGElement with canvas ID {element.canvasID}.")
        self._create_context_menu(event)
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
    def _create_context_menu(self, event):
        """
        Create the contextual menu for the element widgets in the data grid.
        :parameter event: The tkinter event object for the <<ContextMenu>> virtual event
        :return: The tkinter Menu widget that is the contextual menu, as tkinter Menu widget object
        """
        context_menu = tk.Menu(self)
        context_menu.add_command(label='Copy', command=lambda: self._focused_element.elementWidget.event_generate('<<Copy>>'))
        context_menu.add_command(label='Paste', command=lambda: self._focused_element.elementWidget.event_generate('<<Paste>>'))
        # For adding options that do not have a built-in event, use a partial to call a handler method in this tkDataGridWidget class, and pass in the option as an argument to the handler method.
        # TODO: Generalize by passing in a dictionary to the tkDataGridWidget constructor that defines labels and handlers.
        for i in ('Placeholder 1', 'Placeholder 2'):
             context_menu.add_command(label=i, command=partial(self.onContextMenuOptionSelected, i))
        context_menu.post(event.x_root, event.y_root)

    def onContextMenuOptionSelected(self, option):
        """
        Handler for when an option is selected from the contextual menu.
        :parameter option: The option that was selected, as string
        :return: None
        """
        logger = logging.getLogger('tkDataGridWidget_logger')
        logger.debug(f"Context menu option {option} was selected.")
        return None

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
        if self._focused_element is not None:
            (field_name, record_index) = self._get_element_coords(self._focused_element)
            if record_index > 0:
                next_element = self._get_grid_element(field_name, record_index - 1)
                if next_element is not None:
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
        return None

    # TODO: This code throws exception if focus is moved from a field header element, (which can be focused with the mouse).
    def onKeyPressDown(self, event):
        """
        Handler for the down-arrow key press event. Moves focus to the element widget below the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        if self._focused_element is not None:
            (field_name, record_index) = self._get_element_coords(self._focused_element)
            # TODO: This is a bit of a hack, so that if a field header element has focus, the down arrow brings us down
            # to the first record.
            if record_index == None:
                record_index = -1
            if record_index < self._num_records - 1:
                next_element = self._get_grid_element(field_name, record_index + 1)
                if next_element is not None:
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
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
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

    def get_grid_element_value(self, field_name='a_field_name', record_index=0):
        """
        Return the value of the grid element for a given field name and record index. This method is intended
        to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: The value of the grid element for the given field name and record index, or None if no such element exists, as any or None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = self._get_grid_element(field_name, record_index)
        if element is not None:
            return element.get_state()[1]
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
    
    def _get_grid_element(self, field_name='a_field_name', record_index=0):
        """
        Return the tkDGElement object for a given field name and record index.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The (0=based) index of the record, as int
        :return: The tkDGElement object for the given field name and record index, or None if no such element exists, as tkDGElement object or None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = None
        if field_name in self._grid_elements:
            if record_index < len(self._grid_elements[field_name]):
                element = self._grid_elements[field_name][record_index]
        return element

    def get_modified_grid_element_location(self):
        """
        Return the field name and record index for the most recently modified grid element.
        This method is intended to be called by clients, as it does not require clients to interact with tkDGElement objects.
        :return: Tuple (field name, 0-based record index), as (string, int) or None if no such element exists
        """
        (field_name, record_index) = self._get_element_coords(self._modified_element)
        return (field_name, record_index)
    
    def _get_element_coords(self, element=None):
        """
        Return the field name and record index for a given tkDGElement object.
        :parameter element: The tkDGElement object for which to find the field name and record index, as tkDGElement object
        :return: Tuple (field name, 0-based record index), as (string, int) or None if no such element exists
        """
        assert(isinstance(element, tkDGElement))
        if isinstance(element, tkDGElementFieldHeader):
            return (element._raw_state, None)
        else: # NOT a field header element, but a record element
            field_name = ''
            record_index = -1
            for field_name in self._grid_elements:
                if element in self._grid_elements[field_name]:
                    record_index = self._grid_elements[field_name].index(element)
                    break
            if record_index == -1 or field_name == '':
                return None
            else:
                return (field_name, record_index)
        
    def create_element_format(self, format_name = "an_element_format", text_color = 'black', cell_color = 'white',
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

    @property
    def canvas(self):
        return self._dg_canvas

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
        value = element.get_state()[1]
        default_value = element.get_default_value()
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
                    # Iterate through the field's records and perform the unit conversion
                    elem_config = [fc for fc in self._fields_config if fc.fieldName==elem_field][0]
                    # TODO: and clause of if below is NOT OO. Try to improve.
                    if element._raw_state in self._grid_elements and (elem_config.fieldType != FieldType.BOOL):
                        for rec_element in self._grid_elements[element._raw_state]:
                            old_val = rec_element.get_state()[1]
                            new_val = self._uom.convert(hint.prev_unit_id, hint.new_unit_id, old_val)
                            rec_element.set_state(new_val)
        
        # Handle formating the element widget appropriately based on if it has the default value or not.
        elem_config = [fc for fc in self._fields_config if fc.fieldName==elem_field][0]
        if default_value is not None:
            if value is not None:
                
                elem_format = self._element_formats[elem_config.fieldFormat]
                if value == default_value:
                    element._element_widget.configure(background=elem_format[3])
                else:
                    element._element_widget.configure(background=elem_format[1])
        
        self._modified_element = element
        self.notify()
        self._modified_element = None
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
