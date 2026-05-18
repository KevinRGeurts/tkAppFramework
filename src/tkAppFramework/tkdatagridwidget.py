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
from tkinter.messagebox import showerror
from functools import partial
from enum import IntEnum

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError


class FieldType(IntEnum):
    """
    This IntEnum class is used to specify the type of each field when configuring the tkDataGridWidget.
    It actually makes sense to use an Enum here, so that clients do not need to know about the hierarchy of
    tkDGElement classes to specify field types.
    """
    BOOL = 1
    LIST = 2
    TEXT = 3
    # Add more field types as needed


class tkDGElement(Subject):
    """
    Class is the base class for classes that represent an element of a tkDataGridWidget. Class is a subject in Observer
    design pattern, in anticipation of being observed by tkDataGridWidet class.
    """
    def __init__(self, observer=None):
        """
        :parameter observer: Observer object that observes this tkDGElement object, assumed to be a tkDataGridWidget object
        """
        Subject.__init__(self)
        self.attach(observer)
        self._element_widget = None # The tkinter widget that is the element widget. It is assigned in the child class constructors.
        self._element_value = None # The control variable for the element widget, if needed. It is assigned in the child class constructors.
        self._canvas_id = None

    @property
    def canvasID(self):
        return self._canvas_id

    def get_state(self):
        """
        Get the state of the element.
        Note: Must be extended by child classes, because this base class implementation returns value=None.
        :return: Tuple (element type, element value), as (type, any)
        """
        value = None
        if self._element_value is not None:
            value = self._element_value.get()
        return (type(self), value)

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
        :return None:
        """
        if self._element_widget is not None:
            if disabled:
                self._element_widget['state']=tk.DISABLED
            else:
                self._element_widget['state']=tk.NORMAL
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
        super().__init__(parent)
        self._element_widget = tk.Checkbutton(parent.canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                                              takefocus=1, command=partial(self.onCheckbuttonClicked, self._canvas_id) )
        # Create control variable for the Checkbutton and assign it
        self._element_value = tk.IntVar()
        self._element_widget['variable'] = self._element_value
        # Place the widget on the canvas and store the canvas ID
        self._canvas_id = parent.canvas.create_window(f"{x}i", f"{y}i", height=f"{h}i", width=f"{w}i",
                                                      anchor=tk.NW, window=self._element_widget)

    def onCheckbuttonClicked(self, canvas_id):
        """
        Called when a Checkbutton is clicked.
        :parameter canvas_id: The canvas ID of the element widget that was clicked, as int
        :return: None
        """
        print(f"Checkbutton with canvas ID {canvas_id} was clicked.")
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
        super().__init__(parent)
        options_list = ('Option 1', 'Option 2', 'Option 3') # Temporary list of options, will need to be set by some method in the future 
        # Create control variable for the OptionMenu. It is assigned in the constructor below.
        self._element_value = tk.StringVar()
        self._element_value.set(options_list[1]) # Set default value to first option in list
        self._element_widget = tk.OptionMenu(parent.canvas, self._element_value, command=partial(self.onOptionSelected, self._canvas_id),
                                            *options_list)
        # Use confugure because constructor doesn't take these options.
        self._element_widget.configure(relief="flat", takefocus=1)
        # Place the widget on the canvas and store the canvas ID
        self._canvas_id = parent.canvas.create_window(f"{x}i", f"{y}i", height=f"{h}i", width=f"{w}i",
                                                      anchor=tk.NW, window=self._element_widget)

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
        super().__init__(parent)
        # Create the Entry widget for the element.
        self._element_widget = tk.Entry(parent.canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                                              takefocus=1, validate='focusout')
        # Place the widget on the canvas and store the canvas ID
        self._canvas_id = parent.canvas.create_window(f"{x}i", f"{y}i", height=f"{h}i", width=f"{w}i",
                                                      anchor=tk.NW, window=self._element_widget)
        # Register the OnEntryChanged and OnInvalidEntryChange methods with tkinter.
        OnEntryChangedCommand = self._element_widget.register(partial(self.OnEntryChanged, self._canvas_id))
        OnInvalidEntryChangeCommand = self._element_widget.register(self.OnInvalidEntryChange)
        # Congigure the Entry widget to call the appropriate method when a change is made to the text entry.
        self._element_widget.configure(validatecommand=OnEntryChangedCommand)
        self._element_widget.configure(invalidcommand=OnInvalidEntryChangeCommand)
        # Create control variable for the Entry and assign it
        self._element_value = tk.StringVar()
        self._element_widget['textvariable'] = self._element_value
        self._entry_is_valid = True

    def OnEntryChanged(self, canvas_id):
        """
        Event handler for changes to text entry.
        :parameter canvas_id: The canvas ID of the element widget into which text was entered, as int
        :return True: if text entry change is valid, False if invalid, boolean
        """
        # Inform all observers of the change in the text entry
        try:
            # Validity here is an assumption only. If it isn't a good assumption, exception will be raised
            # when notify() is called, and OnInvalidEntryChange() will correct to False.
            print(f"Entry with canvas ID {canvas_id} was changed.")
            self._entry_is_valid = True
            self.notify()
            return True
        except tkDGElementTextInvalidEntryError as e:
            showerror(title='Data Grid Text Entry Error', message=e.error_msg, parent=self.parent)
            return False

    def OnInvalidEntryChange(self):
        """
        Called when OnEntryChanged returns False.
        :return None:
        """
        self._entry_is_valid = False
        self.notify()
        return None

    def set_state(self, value=None):
        """
        Set the state of the text element.
        :paramter value: The value to set in the element.
        :return: None
        """
        assert(type(value)==str)
        self._element_value.set(value)
        super().set_state()
        return None


class tkDGElementFieldHeader(tkDGElement):
    """
    Class represents a field header element of a tkDataGridWidget.
    """
    def __init__(self, parent, x=0.0, y=0.0, w=1.0, h=0.25):
        """
        :parameter parent: tkinter widget that is the parent of this widget, assumed to be a tkDataGridWidget
        :paramter x: The upper-left corner x-coordinate of the element in the data grid in inches, as float
        :paramter y: The upper-left corner y-coordinate of the element in the data grid in inches, as float
        :paramter w: The width of the element in the data grid in inches, as float
        :paramter h: The height of the element in the data grid in inches, as float
        """
        super().__init__(parent)
        # Create the Entry widget for the element.
        self._element_widget = tk.Entry(parent.canvas, justify=tk.CENTER, borderwidth=0, relief="flat",
                                              takefocus=1, validate='focusout')
        # Place the widget on the canvas and store the canvas ID
        self._canvas_id = parent.canvas.create_window(f"{x}i", f"{y}i", height=f"{h}i", width=f"{w}i",
                                                      anchor=tk.NW, window=self._element_widget)
        # Create control variable for the Entry and assign it
        self._element_value = tk.StringVar()
        self._element_widget['textvariable'] = self._element_value
        self._entry_is_valid = True

    def set_state(self, value=None):
        """
        Set the state of the text element.
        :paramter value: The value to set in the element.
        :return: None
        """
        assert(type(value)==str)
        self._element_value.set(value)
        super().set_state()
        return None


class tkDataGridWidget(Subject, Observer, ttk.Labelframe):
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
        :parameter fields_config: List of tuples (field name, FieldType Enum value, field format), as [(string, int, string)]
             note: Field format is a string that is the key to look up in the _element_formats dictionary for formatting element widgets in the data grid.
        :parameter num_records: The number of records to display in the data grid, as int
        """
        Subject.__init__(self)
        Observer.__init__(self)
        ttk.Labelframe.__init__(self, parent, text=title)

        # Dictionary of element format configurations, where Key=format name as string, Value=configuration tuple (text color, cell color, read only), as (string, (string, string, boolean))
        self._element_formats = {}
        self.create_element_format(format_name='field_header', text_color='black', cell_color='#808080', read_only=True)
        self.create_element_format(format_name='editable', text_color='black', cell_color='white', read_only=False)
        self.create_element_format(format_name='read_only', text_color='black', cell_color='cyan', read_only=True)
        self.create_element_format(format_name='default_value', text_color='black', cell_color='green', read_only=False)

        # Add a binding for window destruction, so that this tkDataGridWidget can detach itself from its subjects when it is destroyed.
        self.bind('<Destroy>', self.onDestroy, '+')

        # Store fields and records configuraton info as class attributes.
        assert(type(num_records)==int)
        self._num_records = num_records
        assert(type(fields_config)==list)
        self._fields_config = fields_config

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

        # TODO: These should NOT be bind_all() calls. Investigate what else will work.
        # TODO: Will also need to respond to focus-in and focus-out events, so that self._focused_element is
        # correctly maintained, for example when mousing around.
        # Add some key bindings.
        self.bind_all('<KeyPress-Up>', self.onKeyPressUp)
        self.bind_all('<KeyPress-Down>', self.onKeyPressDown)
        self.bind_all('<KeyPress-Right>', self.onKeyPressRight)
        self.bind_all('<KeyPress-Left>', self.onKeyPressLeft)

        # Store currently focused element widget, as tkDGElement object.
        self._focused_element = None
        # Store most recently modified element widget, as tkDGElement object.
        self._modified_element = None

        # Set up the data grid with the appropriate number of records and fields.
        self._draw_element_separator_lines()
        self._setup_data_grid()

    def onKeyPressUp(self, event):
        """
        Handler for the up-arrow key press event. Moves focus to the element widget above the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        if self._focused_element is not None:
            (field_name, record_index) = self.get_element_coords(self._focused_element)
            if record_index > 0:
                next_element = self.get_grid_element(field_name, record_index - 1)
                if next_element is not None:
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
        return None

    def onKeyPressDown(self, event):
        """
        Handler for the down-arrow key press event. Moves focus to the element widget below the currently focused element widget, if it exists.
        :parameter event: The tkinter event object for the key press event
        :return: None
        """
        if self._focused_element is not None:
            (field_name, record_index) = self.get_element_coords(self._focused_element)
            if record_index < self._num_records - 1:
                next_element = self.get_grid_element(field_name, record_index + 1)
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
            (field_name, record_index) = self.get_element_coords(self._focused_element)
            field_config = [fc for fc in self._fields_config if fc[0]==field_name]
            field_index = self._fields_config.index(field_config[0])
            if field_index < len(self._fields_config) - 1:
                next_element = self.get_grid_element(self._fields_config[field_index+1][0], record_index)
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
            (field_name, record_index) = self.get_element_coords(self._focused_element)
            field_config = [fc for fc in self._fields_config if fc[0]==field_name]
            field_index = self._fields_config.index(field_config[0])
            if field_index > 0:
                next_element = self.get_grid_element(self._fields_config[field_index-1][0], record_index)
                if next_element is not None:
                    next_element._element_widget.focus_set()
                    self._focused_element = next_element
        return None

    def get_grid_element(self, field_name='a_field_name', record_index=0):
        """
        Return the tkDGElement object for a given field name and record index.
        :parameter field_name: The name of the field, as string
        :parameter record_index: The index of the record, as int
        :return: The tkDGElement object for the given field name and record index, or None if no such element exists, as tkDGElement object or None
        """
        assert(type(field_name)==str)
        assert(type(record_index)==int)
        element = None
        if field_name in self._grid_elements:
            if record_index < len(self._grid_elements[field_name]):
                element = self._grid_elements[field_name][record_index]
        return element

    def get_element_coords(self, element=None):
        """
        Return the field name and record index for a given tkDGElement object.
        :parameter element: The tkDGElement object for which to find the field name and record index, as tkDGElement object
        :return: Tuple (field name, record index), as (string, int) or None if no such element exists
        """
        assert(isinstance(element, tkDGElement))
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
        
    def create_element_format(self, format_name = "an_element_format", text_color = 'black', cell_color = 'white', read_only = True):
        """
        Create a named configuration for formatting element widgets in the data grid.
        :parameter format_name: The name of the format, as string
        :parameter text_color: The color of the text in the element widget, as string
        :parameter cell_color: The background color of the element widget, as string
        :parameter read_only: If True, the element widget will not accept input, as boolean
        """
        assert(type(format_name)==str)
        assert(type(text_color)==str)
        assert(type(cell_color)==str)
        assert(type(read_only)==bool)
        self._element_formats[format_name] = (text_color, cell_color, read_only)
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
            text_color, cell_color, read_only = self._element_formats[elem_format]
            element.disable_element(read_only)
            element._element_widget.configure(background=cell_color, highlightcolor=cell_color, foreground=text_color)
        return None

    # TODO: Refactor so that this method calls _apply_element_format_to_one_element() for each element, instead of having the formatting code in both methods.
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
            text_color, cell_color, read_only = self._element_formats[format_name]
            if field_name in self._grid_elements:
                for element in self._grid_elements[field_name]:
                    element._element_widget.configure(background=cell_color, highlightcolor=cell_color, foreground=text_color)
                    # TODO: Fix this horribly non-OO code.
                    if element.get_state()[0] == tkDGElementFieldHeader:
                        element._element_widget.configure(font=('TkDefaultFont', 10, 'bold'))
                    if element.get_state()[0] == tkDGElementText:
                        element._element_widget.configure(readonlybackground=cell_color)
                    element.disable_element(read_only)
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

    def handle_element_update(self, element):
        """
        Handler function called when a tkDGElement object notifies the tkDataGridWidget of a change in state.
        parameter element: The tkDGElement object that is notifying the tkDataGridWidget of a change in state, as tkDGElement object
        :return None:
        """
        value = element.get_state()
        print(f"tkDataGridWidget received update from tkDGElement with canvas ID {element.canvasID}. Elements state is {value}.")
        self._modified_element = element
        self.notify()
        self._modified_element = None
        return None
        
    # TODO: Enhance so that fields can be columns instead of rows.
    def _draw_element_separator_lines(self):
        """
        This utility function is used to draw the lines on the canvas which visuall separate the elements
        into a grid.
        :return: None
        """
        # First, draw vertical lines to separate fields/columns.
        # Coordinate (canvas?) where next line should start, in inches
        start_x = 0.0
        start_y = 0.0
        # Remember that we need to account for the field header row, hence the +1's and +2's below.
        end_y = ((self._num_records+1) * self._row_h) + ((self._num_records+2)*self._sep_w)
        for field_i in range(len(self._fields_config) + 1):
                self._dg_canvas.create_line(f"{start_x}i", f"{start_y}i", f"{start_x}i", f"{end_y}i",
                                            width=f"{self._sep_w}i", tags='tag_element_separator_line')
                start_x += self._col_w + self._sep_w
        # Second, draw horizontal lines to separate records/rows.
        start_x = 0.0
        end_x = (len(self._fields_config) * self._col_w) + ((len(self._fields_config) +1)*self._sep_w)
        start_y = 0.0
        for rec_i in range(self._num_records + 2):
                self._dg_canvas.create_line(f"{start_x}i", f"{start_y}i", f"{end_x}i", f"{start_y}i",
                                            width=f"{self._sep_w}i", tags='tag_element_separator_line')
                start_y += self._row_h + self._sep_w

        return None
    
    # TODO: Enhance so that fields can be columns instead of rows.
    def _setup_data_grid(self):
        """
        Set up the data grid with the appropriate array of tkDGElement widgets for the fields and records.
        :return: None
        """
        # Coordinate (canvas?) where next widget shoud be inserted, in inches
        # Must set width and height for all widgets, so that these coordinates can be appropriately updated.
        next_x = 0.0 + self._sep_w
        next_y = 0.0 + self._sep_w
        # Widget height and width, in inches
        wid_h = self._row_h 
        wid_w = self._col_w
        # Add widgets...
        upper_left_element = None
        for field in self._fields_config:
            # TODO: Use field name in a not yet created header row.
            field_name = field[0]
            field_type = field[1]
            field_format = field[2]
            # Handle the field header element for this field/column.
            element = tkDGElementFieldHeader(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
            self.register_subject(element, partial(self.handle_element_update, element))
            element.set_state(field_name)
            self._apply_element_format_to_one_element('field_header', element)
            next_y += wid_h + self._sep_w
            # End handling the field header element for this field/column.
            rec_list = []
            for rec_i in range(self._num_records):
                # TODO: Well, this is ugly, non-OO code...
                element = None
                match field_type:
                    case FieldType.BOOL:
                        element = tkDGElementBool(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.LIST:
                        element = tkDGElementList(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                    case FieldType.TEXT:
                        element = tkDGElementText(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
                # Tag the element's canvas ID with the field name, so we can "adress" all of a field's elements as a group.
                # TODO: This may turn out to not actually be useful/needed.
                self._dg_canvas.addtag_withtag(f"tag_{field_name}", element.canvasID)
                if upper_left_element is None:
                    upper_left_element = element
                self.register_subject(element, partial(self.handle_element_update, element))
                self._wids.append(element.canvasID)
                rec_list.append(element)
                # We will stack the elements vertically, so only update next_y.
                next_y += wid_h + self._sep_w
            # Store the list of tkDGElement objects for this field in the _grid_elements dictionary.
            self._grid_elements[field_name] = rec_list
            # Configure the field's element widgets with the appropriate format.
            self._apply_element_format_to_field_elements(field_format, field_name)
            # Moving to the next field/column, so update next_x and reset next_y.
            next_x += wid_w + self._sep_w
            next_y = 0.0 + self._sep_w 
        # Now some temporary code where we can just try stuff out as we learn.
        # ...
        
        # Set focus to upper left widget in data grid, if it exists.
        if upper_left_element is not None:
            upper_left_element._element_widget.focus_set()
            self._focused_element = upper_left_element

        return None

    
