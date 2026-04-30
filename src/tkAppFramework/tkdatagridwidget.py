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

# Local imports
from tkAppFramework.ObserverPatternBase import Subject, Observer


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
        self._element_widget = tk.Checkbutton(self, justify=tk.CENTER, borderwidth=0, relief="flat", highlightcolor="cyan", background="cyan", takefocus=1)
        self._element_widget.grid(column=0, row=0, sticky='NWSE')
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2
        # Create control variable for the Checkbutton and assign it
        self._element_value = tk.IntVar()
        self._element_widget['variable'] = self._element_value

    def get_state(self):
        """
        Get the state of the boolean element.
        :return: Tuple (element type, element value), as (type, any)
        """
        elem_type = super().get_state()
        value = self._element_value.get()
        return (elem_type, value)

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
        self._element_widget = tk.OptionMenu(self, self._element_value, *options_list)
        self._element_widget.configure(relief="flat", highlightcolor="green", background="green", takefocus=1)
        self._element_widget.grid(column=0, row=0, sticky='NWSE')
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

    def get_state(self):
        """
        Get the state of the list element.
        :return: Tuple (element type, element value), as (type, any)
        """
        elem_type = super().get_state()
        value = self._element_value.get()
        return (elem_type, value)

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


class tkDataGridWidget(ttk.Labelframe, Subject, Observer):
    """
    Class represents a tkinter label frame, the widget contents of which allow displayinbg and interacting with
    data records and fields. Class is a Subject in Observer design pattern so that it can be observed by a tkViewManager object.
    Class is an Observer in Observer design pattern so that it can observe tkDGElement objects.
    """
    def __init__(self, parent, title='Data Grid') -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter title: The text label of the Labelframe, as string
        """
        ttk.Labelframe.__init__(self, parent, text=title)
        Subject.__init__(self)
        Observer.__init__(self)

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

        # Call the temp function that does some useful things while I'm learning.
        self.test_data_grid()

    @property
    def canvas(self):
        return self._dg_canvas
        
    def test_data_grid(self):
        """
        This is a temporary function, while I learn how widgets are placed into a Canvas.
        """
        # Coordinate (canvas?) where next widget shoud be inserted, in inches
        # Must set width and height for all widgets, so that these coordinates can be appropriately updated.
        next_x = 0.0
        next_y = 0.0
        # Widget width and height, in inches
        wid_h = 0.25 
        wid_w = 1.0
        # Add widgets...
        # List of widget ID's
        wids = []
        # Make some entry widgets and insert them into the canvas
        for i in range(25):
            te = ttk.Entry(self._dg_canvas)
            te.insert(index=0, string=f"Text Data {i}")
            te_id = self._dg_canvas.create_window(f"{next_x}i", f"{next_y}i", height=f"{wid_h}i", width=f"{wid_w}i",
                                                  anchor=tk.NW, window=te)
            wids.append(te_id)
            # We will stack the widgets vertically, so only update next_y.
            next_y += wid_h
        # Make some tkDGElementBool widgets and insert them into the canvas as a second column
        next_x += wid_w
        next_y = 0.0
        for i in range(25):
            be = tkDGElementBool(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
            wids.append(be.canvasID)
            # We will stack the widgets vertically, so only update next_y.
            next_y += wid_h
        # Make some tkDGElementList widgets and insert them into the canvas as a third column
        next_x += wid_w
        next_y = 0.0
        for i in range(25):
            le = tkDGElementList(self, x=next_x, y=next_y, w=wid_w, h=wid_h)
            wids.append(le.canvasID)
            # We will stack the widgets vertically, so only update next_y.
            next_y += wid_h

        return None

    
