"""
This module defines the tkDataGridFigureWidget and DataGridFigureTemplate classes. Together they use the matplotlib module to
display graphical figures (line plots and bar plots, for example) of a data grid's records and fields.

Exported Classes:
    tkDataGridFigureWidget -- Displays a matplotlib figure in a tkinter Frame widget, with a DataGridFigureTemplate object to define the figure contents.
    DataGridFigureTemplate -- Base class for children which are responsible for actually making a specific matplotlib figure.
    ScatterPlotFieldsFigureTemplate -- Child of DataGridFigureTemplate that makes a scatter plot of two or more fields in the data grid.
    BarPlotFieldsFigureTemplate -- Child of DataGridFigureTemplate that makes a bar plot of two or more fields in the data grid.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk


# 3rd party package imports (e.g., from PyPi)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Local imports
from tkAppFramework.ObserverPatternBase import Subject


class DataGridFigureTemplate(object):
    """
    Base class for children which are responsible for actually making a specific matplotlib figure on
    behalf of a tkDataGridFigureWidget object.
    """
    def __init__(self, x_label = '', y_label = ''):
        """
        :parameter x_label: Text label to place on the figure's x-axis, as string
        :parameter y_label: Text label to place on the figure's y-axis, as string
        """
        assert(isinstance(x_label, str))
        self._x_label = x_label
        assert(isinstance(y_label, str))
        self._y_label = y_label

    def make_figure(self, figure_widget):
        """
        Make the figure with calls to matplotlib, relying on calls to figure_widget to obtain required data values.
        Must be extended by child classes to actually make the figure. This base class method sets the axes labels and aspect ratio.
        :parameter figure_widget: The figure widget to use to obtain data values and to make the plot. 
        :return: None
        """
        assert(isinstance(figure_widget, tkDataGridFigureWidget))
        figure_widget.axes.set_aspect("auto")

        # x-axis label
        _dg=figure_widget.master
        if _dg.get_field_unitID(self._x_label) is not None:
            _x_label = f"{self._x_label} ({_dg.get_field_unit_name(self._x_label)})"
        else:
            _x_label = f"{self._x_label}"
        figure_widget.axes.set_xlabel(_x_label)

        figure_widget.axes.set_ylabel(self._y_label)
        figure_widget.axes.use_sticky_edges = True
        return None


class ScatterPlotFieldsFigureTemplate(DataGridFigureTemplate):
    """
    Child of DataGridFigureTemplate that makes a scatter plot of two or more fields in the data grid.
    """
    def __init__(self, x_label='', y_label='', x_field='', y_fields=[], symbols=[]):
        """
        :parameter x_label: Text label to place on the figure's x-axis, as string
        :parameter y_label: Text label to place on the figure's y-axis, as string
        :parammeter x_field: Name of the field in the data grid to use for the x-axis values, as string
        :parameter y_fields: List of names of the fields in the data grid to use for the y-axis values, as list of strings
        :parameter symbols: List of matplotlib symbols (e.g. 'bo-' for blue circles connected with a solid line) to use for each y_field, as list of strings
        """
        assert(isinstance(x_label, str))
        self._x_label = x_label
        assert(isinstance(y_label, str))
        self._y_label = y_label
        assert(isinstance(x_field, str))
        self._x_field = x_field
        assert(isinstance(y_fields, list))
        for yf in y_fields:
            assert(isinstance(yf, str))
        self._y_fields = y_fields
        assert(isinstance(symbols, list))
        for sym in symbols:
            assert(isinstance(sym, str))
        self._symbols = symbols
        
    def make_figure(self, figure_widget):
        """
        Make the figure with calls to matplotlib, relying on calls to figure_widget to obtain required data values.
        :parameter figure_widget: The figure widget to use to obtain data values and to make the plot. 
        :return: None
        """
        super().make_figure(figure_widget)
        for yf, sym in zip(self._y_fields, self._symbols):
            xvals=[]
            yvals=[]
            _dg=figure_widget.master
            for reci in range(_dg.num_records):
                xvals.append(_dg.get_grid_element_value_display_units(self._x_field, reci))
                yvals.append(_dg.get_grid_element_value_display_units(yf, reci))
            if _dg.get_field_unitID(yf) is not None:
                _leg = f"{yf} ({_dg.get_field_unit_name(yf)})"
            else:
                _leg = f"{yf})"
            graph = figure_widget.axes.plot(xvals, yvals, sym, label=_leg)
        figure_widget.axes.legend()
        figure_widget.axes.grid(visible=True, which='major')
        return None


class BarPlotFieldsFigureTemplate(DataGridFigureTemplate):
    """
    Child of DataGridFigureTemplate that makes a bar plot of two or more fields in the data grid.
    """
    def __init__(self, x_label='', y_label='', x_field='', y_fields=[], colors=[]):
        """
        :parameter x_label: Text label to place on the figure's x-axis, as string
        :parameter y_label: Text label to place on the figure's y-axis, as string
        :parammeter x_field: Name of the field in the data grid to use for the x-axis values, as string
        :parameter y_fields: List of names of the fields in the data grid to use for the y-axis values, as list of strings
        :parameter colors: List of matplotlib colors (e.g. 'b' for blue bars) to use for each y_field, as list of any valid matplotlib color format
        """
        assert(isinstance(x_label, str))
        self._x_label = x_label
        assert(isinstance(y_label, str))
        self._y_label = y_label
        assert(isinstance(x_field, str))
        self._x_field = x_field
        assert(isinstance(y_fields, list))
        for yf in y_fields:
            assert(isinstance(yf, str))
        self._y_fields = y_fields
        assert(isinstance(colors, list))
        self._colors = colors
        
    def make_figure(self, figure_widget):
        """
        Make the figure with calls to matplotlib, relying on calls to figure_widget to obtain required data values.
        :parameter figure_widget: The figure widget to use to obtain data values and to make the plot. 
        :return: None
        """
        super().make_figure(figure_widget)
        # Get the data grid widget associated with the figure
        _dg=figure_widget.master
        # Get the tick labels for the groups of bars
        xvals=[]
        for reci in range(_dg.num_records):
            # Note the conversion to string, as bars are for "category data"
            xvals.append(str(_dg.get_grid_element_value_display_units(self._x_field, reci)))
        # Get the heights of the bars, packaged as a dictionary, where keys are the legend and values
        # are the bar heights
        _heights={}
        _colors=[]
        for yf, color in zip(self._y_fields, self._colors):
            yvals=[]
            if _dg.get_field_unitID(yf) is not None:
                _leg = f"{yf} ({_dg.get_field_unit_name(yf)})"
            else:
                _leg = f"{yf})"
            for reci in range(_dg.num_records):
                y = _dg.get_grid_element_value_display_units(yf, reci)
                if y is None:
                    y = float('nan')
                yvals.append(y)
            _heights[_leg]=yvals
            _colors.append(color)
        graph = figure_widget.axes.grouped_bar(heights=_heights, tick_labels=xvals, colors=_colors)
        figure_widget.axes.legend()
        figure_widget.axes.grid(visible=True, which='major')
        return None


class tkDataGridFigureWidget(Subject, ttk.Frame):
    """
    Class represents a tkinter Frame, the widget contents of which display a matplotlib figure.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget, in this case the tkDataGridWidget
        """
        ttk.Frame.__init__(self, parent)
        Subject.__init__(self)
        self._CreateWidgets()

    def _CreateWidgets(self):
        """
        This method is called by __init__() to create the child widgets of the tkDataGridGraphWidget.
        :return None:
        """
        # Make a matplotlib Figure that will be added to the matplotlib FigureCanvasTkAgg below,
        # and give it an axes.
        self._figure = Figure(figsize=(5,4), dpi=100) # figsize=(width in inches, height in inches)
        self._ax = self._figure.add_subplot()
        
        self._mpl_figure_canvas = FigureCanvasTkAgg(self._figure, self)
        self._mpl_figure_canvas.get_tk_widget().grid(column=0, row=0, columnspan=2, sticky='NWES') # Grid-3
        self.columnconfigure(0, weight=1) # Grid-3
        self.rowconfigure(0, weight=1) # Grid-3
        # Capture key press events so user can 'escape' back to the data grid.
        self._mpl_figure_canvas.mpl_connect('key_press_event', self._on_key_press)

        return None

    @property
    def axes(self):
        """
        Return the axes object for the matplotlib figure.
        """
        return self._ax

    def _on_key_press(self, event):
        """
        Handler called when matplotlib figure canvas receives a key press event.
        """
        if event.key == 'escape':
            # master is the tkDataGridWidget
            self.master._figure_asks_show_grid()

    def focus_figure_canvas(self):
        """
        Call this function if you want the tkinter widget for the matplotlib figure canvas to request focus.
        :return None:
        """
        self._mpl_figure_canvas.get_tk_widget().focus_set()
        return None

    def draw_figure(self, template):
        """
        Draw the matplotlib figure using paramter figure template.
        :paramter template: Figure template to use to make the figure, as DataGridFigureTemplate object
        :return: None
        """
        assert(isinstance(template, DataGridFigureTemplate))
         # Clear the axes in case we've been here before.
        self._ax.cla()
        template.make_figure(self)
        # Put some text on the figure to tell the user how to return to the data grid.
        self._figure.text(0.05, 0.95, 'Press escape key to return to data grid.', fontsize=8)
        # Actually draw the figure
        self._mpl_figure_canvas.draw()
        return None
