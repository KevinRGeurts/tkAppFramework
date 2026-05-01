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
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from functools import partial
from enum import IntEnum

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer


class FieldType(IntEnum):
    """
    This IntEnum class is used to specify the type of each field when configuring the tkDataGridWidget.
    It actually makes sense to use an Enum here, so that clients do not need to know about the hierarchy of
    tkDGElement classes to specify field types.
    """
    BOOL = 1
    LIST = 2
    NUMBER = 3
    # Add more field types as needed


# TODO: The Frame is used to create a border around the element in the canvas. Consider if it would be better to draw
# a border within the canvas using lines. This might eliminate the need for the Frame and, for example, make focus
# traversal work better.
class tkDGElement(tk.Frame, Subject):
    """
    Class is the base class for classes that represent an element of a tkDataGridWidget. Class is a subject in Observer
    design pattern, in anticipation of being observed by tkDataGridWidet class.
    """
    def __init__(self, parent=None, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter parent: tkinter widget that is the parent of this element, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        """
        tk.Frame.__init__(self, parent.canvas, highlightbackground="black", highlightcolor="black", highlightthickness=1, bd=0, takefocus=1)
        Subject.__init__(self)
        self.attach(parent)
        self._element_widget = None # The "useful" widget, not the border creating Frame
        self._canvas_id = parent.canvas.create_window(f"{x}i", f"{y}i", height=f"{h}i", width=f"{w}i",
                                                      anchor=tk.NW, window=self)

    @property
    def canvasID(self):
        return self._canvas_id

    def get_state(self):
        """
        Get the state of the element.
        Note: Must be extended by child classes, because this base class implementation returns value=None.
        :return: Tuple (element type, element value), as (type, any)
        """
        return (type(self), None)

    def set_state(self, value=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element.
        Note: Must be extended by child classes, because this base class implementation does nothing with value parameter.
              It does, however, call self.notify(), so when extending, call the base class implementation at the end of the extended method.
        :return: None
        """
        self.notify()
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        Note: Must be implemented by child classes, because this base clas implementation will raise NotImplementedError if called.
        :return None:
        """
        raise NotImplementedError
        return None


class tkDGElementBool(tkDGElement):
    """
    Class represents a boolean element of a tkDataGridWidget.
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
        self._element_widget = tk.Checkbutton(self, justify=tk.CENTER, borderwidth=0, relief="flat", highlightcolor="cyan",
                                              background="cyan", takefocus=1, command=partial(self.onCheckbuttonClicked, self._canvas_id) )
        self._element_widget.grid(column=0, row=0, sticky='NWSE')
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2
        # Create control variable for the Checkbutton and assign it
        self._element_value = tk.IntVar()
        self._element_widget['variable'] = self._element_value

    def onCheckbuttonClicked(self, canvas_id):
        """
        Called when a Checkbutton is clicked.
        :parameter canvas_id: The canvas ID of the element widget that was clicked, as int
        :return: None
        """
        print(f"Checkbutton with canvas ID {canvas_id} was clicked.")
        self.notify()
        return None

    def get_state(self):
        """
        Get the state of the boolean element.
        :return: Tuple (element type, element value), as (type, any)
        """
        elem_type = super().get_state()
        value = self._element_value.get()
        return (elem_type[0], value)

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

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._element_widget['state']=tk.DISABLED
        else:
            self._element_widget['state']=tk.NORMAL
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
        options_list = ('Option 1', 'Option 2', 'Option 3') # Temporary list of options, will need to be set by some method in the future 
        # Create control variable for the OptionMenu. It is assigned in the construcgtor.
        self._element_value = tk.StringVar()
        self._element_value.set(options_list[1]) # Set default value to first option in list
        self._element_widget = tk.OptionMenu(self, self._element_value, command=partial(self.onOptionSelected, self._canvas_id),
                                            *options_list)
        self._element_widget.configure(relief="flat", highlightcolor="green", background="green", takefocus=1)
        self._element_widget.grid(column=0, row=0, sticky='NWSE')
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

    def onOptionSelected(self, canvas_id, option):
        """
        Called when an OptionMenu selection is made.
        :parameter canvas_id: The canvas ID of the element widget that had an option selected, as int
        :paramter option: The option selected, as string
        :return: None
        """
        print(f"OptionMenu with canvas ID {canvas_id} had option {option} selected.")
        self.notify()
        return None

    def get_state(self):
        """
        Get the state of the list element.
        :return: Tuple (element type, element value), as (type, any)
        """
        elem_type = super().get_state()
        value = self._element_value.get()
        return (elem_type[0], value)

    def set_state(self, value=None):
        """
        Set the state of the element.
        :paramter value: The value to set in the element.
        Note: Must be extended by child classes, because this base class implementation does nothing with value parameter.
              It does, however, call self.notify(), so when extending, call the base class implementation at the end of the extended method.
        :return: None
        """
        assert(type(value)==str)
        self._element_value.set(value)
        super().set_state()
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._element_widget['state']=tk.DISABLED
        else:
            self._element_widget['state']=tk.NORMAL
        return None


class tkDGElementNumber(tkDGElement):
    """
    Class represents a number containing (int or float) element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25, min_val=None, max_val=None):
        """
        :parameter parent: tkinter widget that is the parent of this widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        :parameter min_val: The minimum value that can be entered in the element, as int or float
        :parameter max_val: The maximum value that can be entered in the element, as int or float
        """
        super().__init__(parent, x, y, w, h)
        self._element_widget = tk.Entry(self, justify=tk.CENTER, borderwidth=0, relief="flat", highlightcolor="white",
                                              background="white", takefocus=1)
        self._element_widget.grid(column=0, row=0, sticky='NWSE')
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2
        # Create control variable for the Entry and assign it
        self._element_value = tk.StringVar()
        self._element_widget['textvariable'] = self._element_value

    # def onCheckbuttonClicked(self, canvas_id):
    #     """
    #     Called when a Checkbutton is clicked.
    #     :parameter canvas_id: The canvas ID of the element widget that was clicked, as int
    #     :return: None
    #     """
    #     print(f"Checkbutton with canvas ID {canvas_id} was clicked.")
    #     self.notify()
    #     return None

    def get_state(self):
        """
        Get the state of the number element.
        :return: Tuple (element type, element value), as (type, float or int)
        """
        elem_type = super().get_state()
        value = self._element_value.get()
        return (elem_type[0], value)

    def set_state(self, value=None):
        """
        Set the state of the number element.
        :paramter value: The value to set in the element.
        :return: None
        """
        assert(type(value)==int or type(value)==float)
        self._element_value.set(value)
        super().set_state()
        return None

    def disable_element(self, disabled=True):
        """
        Used to set if the element widget will accept input.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._element_widget['state']=tk.DISABLED
        else:
            self._element_widget['state']=tk.NORMAL
        return None


class tkDataGridWidget(ttk.Labelframe, Subject, Observer):
    """
    Class represents a tkinter label frame, the widget contents of which allow displayinbg and interacting with
    data records and fields. Class is a Subject in Observer design pattern so that it can be observed by a tkViewManager object.
    Class is an Observer in Observer design pattern so that it can observe tkDGElement objects.
    """
    # TODO: Pass in row heights and collumn widths?
    def __init__(self, parent, title='Data Grid', fields_config=[], num_records=0) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter title: The text label of the Labelframe, as string
        :parameter fields_config: List of tuples (field name, FieldType Enum value), as [(string, int)]
        :parameter num_records: The number of records to display in the data grid, as int
        """
        ttk.Labelframe.__init__(self, parent, text=title)
        Subject.__init__(self)
        Observer.__init__(self)

        # Maintain a dictionary of Key=subject (child widget), Value=update handler callable
        self._subjects = {}

        # Add a binding for window destruction, so that this tkDataGridWidget can detach itself from its subjects when it is destroyed.
        self.bind('<Destroy>', self.onDestroy, '+')

        # Store fields and records configuraton info as class attributes.
        assert(type(num_records)==int)
        self._num_records = num_records
        assert(type(fields_config)==list)
        self._fields_config = fields_config

        # Widget ID's for the widgets in the data grid.
        self._wids = []

        # Canvas row height and column width, in inches.
        self._row_h = 0.25 
        self._col_w = 1.0

        # Note: i=inches
        # Note: scrollregion=(w,n,e,s)
        self._dg_canvas = tk.Canvas(self, width='5i', height='4i', scrollregion=('0i','0i','10i','10i'), background='gray75')
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

        # Set up the data grid with the appropriate number of records and fields.
        self._setup_data_grid()

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
        
    # TODO: Consider if this method should be moved to ObserverPatternBase.Observer class, since it has now been
    # implemented in both tkDataGridWidget and tkViewManager.
    def register_subject(self, subject = None, update_handler = None):
        """
        Register a subject tkDGElement object and the callable to handle subject updates.
        :parameter subject: The tkDGElement, an object of type Subject and type (tkDGElement)
        :parameter update_handler: The callable function to handle updates for the subject
        :return: None
        """
        assert(isinstance(subject, Subject))
        assert(isinstance(subject, tkDGElement))
        assert(callable(update_handler))
        self._subjects[subject]=update_handler
        return None
    
    # TODO: Consider if this method should be moved to ObserverPatternBase.Observer class, since it has now been
    # implemented in both tkDataGridWidget and tkViewManager.
    def _detach_from_subjects(self):
        """
        Detach tkDataGridWidget from all subjects (tkDGElement objects). Called from onDestroy(...).
        :return None:
        """
        for subject in self._subjects:
            subject.detach(self)
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

    @property
    def canvas(self):
        return self._dg_canvas

    def handle_element_update(self, element):
        """
        Handler function called when a tkDGElement object notifies the tkDataGridWidget of a change in state.
        parameter element: The tkDGElement object that is notifying the tkDataGridWidget of a change in state, as tkDGElement object
        :return None:
        """
        value = element.get_state()
        print(f"tkDataGridWidget received update from tkDGElement with canvas ID {element.canvasID}. Elements state is {value}.")
        return None
        
    # TODO: Enhance so that fields can be columns instead of rows.
    def _setup_data_grid(self):
        """
        Set up the data grid with the appropriate array of tkDGElement widgets for the fields and records.
        :return: None
        """
        # Coordinate (canvas?) where next widget shoud be inserted, in inches
        # Must set width and height for all widgets, so that these coordinates can be appropriately updated.
        next_x = 0.0
        next_y = 0.0
        # Widget height and width, in inches
        wid_h = self._row_h 
        wid_w = self._col_w
        # Add widgets...
        for field in self._fields_config:
            # TODO: Use field name in a not yet created header row.
            field_name = field[0]
            field_type = field[1]
            for rec_i in range(self._num_records):
                # TODO: Well, this is ugly, non-OO code...
                element = None
                match field_type:
                    case FieldType.BOOL:
                        element = tkDGElementBool(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.LIST:
                        element = tkDGElementList(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.NUMBER:
                        element = tkDGElementNumber(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                self.register_subject(element, partial(self.handle_element_update, element))
                self._wids.append(element.canvasID)
                # We will stack the elements vertically, so only update next_y.
                next_y += wid_h
            # Moving to the next field/column, so update next_x and reset next_y.
            next_x += wid_w
            next_y = 0.0
        # Now some temporary code where we can just try stuff out as we learn.

        return None

    
