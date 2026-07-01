"""
This module defines the tkDataGridFigureWidget class. It is a tkinter widget that uses a the matplotlib module to
display graphical figures (line plots and bar plots, for example) of a data grid's records and fields.

Exported Classes:
    tkDataGridFigureWidget -- Blah, blah, blah.

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
        :parameter figure_widget: The tkDataGridFigureWidget object which HAS this DataGridFigureTemplate object.
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
        :parameter figure_widget: The figure widget to use to obtain data values and to make the plot. 
        :return: None
        """
        assert(isinstance(figure_widget, tkDataGridFigureWidget))
        
        figure_widget._ax.cla() # Clear the axes for the next time through...
        
        # Provide axis labels
        figure_widget.axes.set_aspect("equal")
        figure_widget.axes.set_xlabel(self._x_label)
        figure_widget.axes.set_ylabel(self._y_label)
        figure_widget.axes.use_sticky_edges = True
        
        # TODO: Move to child
        # Create the data set to plot
        # x = [1, 2, 3, 4, 5]
        # y= [1, 4, 9, 16, 25]
        # graph = self._figure_widget._ax.plot(x, y, 'bo')

        # Actually draw the figure
        # figure_widget._mpl_figure_canvas.draw()

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
        template.make_figure(self)
        # Put some text on the figure to tell the user how to return to the data grid.
        self._ax.text(0.05, 0.95, 'Press escape key to return to data grid.', transform=self._ax.transAxes,
                      fontsize=8, verticalalignment='top')
        return None
