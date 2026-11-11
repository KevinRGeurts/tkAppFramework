"""
This module defines the tkBuildFigureDlg class.
It is a concrete implementation of the tkModalDialog class that enables the user to construct an instance of one of the children of DataGridFigureTemplate.

Exported Classes:
    tkBuildFigureDlg -- A concrete implementation of tkModalDialog that enables the user to construct an instance
                        of one of the children of DataGridFigureTemplate

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import logging
import sysconfig
import tkinter as tk
from tkinter import ttk


# Local imports
from tkAppFramework.tkModalDialog import tkModalDialog


class tkBuildFigureDlg(tkModalDialog):
    """
    This class represents a tkModalDialog that enables the user to construct an instance
    of one of the children of DataGridFigureTemplate.
    """
    def __init__(self, parent, dlg_input={}, apply_callback=None):
        """
        :parameter parent: The parent tkinter window for the dialog
        :param dlg_input: A dictionary of input parameters for the dialog, default is empty dictionary
            'fig_types': The types of figures that can be built, as list of strings (Must be from list ['scatter', 'bar', 'box', 'histogram'].)
            'x_fields': The names of the field(s) that can be used for the x-axis, as string or list of strings
            'y_fields': The name(s) of the field(s) that can be used for the y-axis, as string or list of strings
        :parameter apply_callback: A callable that will be used to build the figure template, as callable
            Note: Should be: tkDataGridWidget._add_graph(dlg_output)
        """
        assert(isinstance(dlg_input, dict))
        self._dlg_input = dlg_input
        assert(callable(apply_callback))
        self._apply_callback = apply_callback
        
        # Call super classes' __init__
        dialog_title = 'Build Data Grid Figure'
        help_file_path = sysconfig.get_path('data') + '\\Help\\tkAppFramework\\BuildFigureDialog_HelpFile.md'
        super().__init__(parent, title = dialog_title, help_file = help_file_path,
                         dlg_input=self._dlg_input, apply_callback=self._apply_callback, log_level = logging.INFO)

    def body(self, master):
        """
        Create dialog body.
        :parameter master: The parent tkinter window for the dialog
        :return: widget that should have initial focus
        This is an override of the base class method, and is called by the Dialog.__init__ method.
        """
        # Create an entry field for the type of figure to build
        self._lbl_figure_type = ttk.Label(master, text="Figure Type:")
        self._lbl_figure_type.pack()
        self._ent_figure_type = tk.Entry(master)
        self._ent_figure_type.pack()
        self._value_figure_type=tk.StringVar()
        self._value_figure_type.set(self._dlg_input['fig_types'][0])
        self._ent_figure_type['textvariable']=self._value_figure_type
        # Create an entry field for the x_field of the figure to build
        self._lbl_x_field = ttk.Label(master, text="X-Axis Field Name:")
        self._lbl_x_field.pack()
        self._ent_x_field = tk.Entry(master)
        self._ent_x_field.pack()
        self._value_x_field=tk.StringVar()
        self._value_x_field.set(self._dlg_input['x_fields'][0])
        self._ent_x_field['textvariable']=self._value_x_field
        # Create an entry field for the y_fields of the figure to build
        self._lbl_y_fields = ttk.Label(master, text="Y-Axis Field Name(s):")
        self._lbl_y_fields.pack()
        self._ent_y_fields = tk.Entry(master)
        self._ent_y_fields.pack()
        self._value_y_fields=tk.StringVar()
        self._value_y_fields.set(self._dlg_input['y_fields'][0])
        self._ent_y_fields['textvariable']=self._value_y_fields
        # Create an entry field for the symbol(s) / color(s) of the figure to build
        self._lbl_symbol_color = ttk.Label(master, text="Symbol(s) / Color(s):")
        self._lbl_symbol_color.pack()
        self._ent_symbol_color = tk.Entry(master)
        self._ent_symbol_color.pack()
        self._value_symbol_color=tk.StringVar()
        self._value_symbol_color.set('bo-')
        self._ent_symbol_color['textvariable']=self._value_symbol_color
        
        return self._ent_figure_type  # initial focus

    def _get_dialog_output_dict(self):
        """
        This method is an override of the base class method and is called by apply() to get the dialog output dictionary, which is then passed to the apply callback.
        :return: dlg_output, a dictionary of output results for the dialog, default is empty dictionary.
        """
        # Get the figure type from the entry field
        figure_type = self._value_figure_type.get()
        # Branch on figure type and get other fields as needed.
        # Get the values from the entry fields in the dialog, pack them into a dictionary, and call the apply callback with the dictionary.
        # dlg_output: A dictionary of output results for the dialog, default is empty dictionary.
        #   'fig_type': The type of figure requested to be built, as string (Must be from list ['scatter', 'bar', 'box', 'histogram'].)
        #   'x_field': The name of the field requested to be used for the x-axis, as string
        #   'y_fields': The name(s) of the field(s) requested to be used for the y-axis, as list of strings
        #   'symbol_color': The symbol(s) and or color(s) requested to be used for points/lines/bars, as list of strings
        dlg_output = {'fig_type': figure_type}
        if figure_type in ['scatter', 'bar', 'box', 'histogram']:
            match figure_type:
                case 'scatter':
                    dlg_output['x_field'] = self._value_x_field.get()
                    dlg_output['y_fields'] = self._comma_separated_string_to_list(self._value_y_fields.get())
                    dlg_output['symbol_color'] = self._comma_separated_string_to_list(self._value_symbol_color.get())
                case 'bar':
                    dlg_output['x_field'] = self._value_x_field.get()
                    dlg_output['y_fields'] = self._comma_separated_string_to_list(self._value_y_fields.get())
                    dlg_output['symbol_color'] = self._comma_separated_string_to_list(self._value_symbol_color.get())
                case 'box':
                    dlg_output['x_field'] = None
                    dlg_output['y_fields'] = self._comma_separated_string_to_list(self._value_y_fields.get())
                    dlg_output['symbol_color'] = None
                case 'histogram':
                    dlg_output['x_field'] = None
                    dlg_output['y_fields'] = self._comma_separated_string_to_list(self._value_y_fields.get())[0]
                    dlg_output['symbol_color'] = None
        else:
            dlg_output['x_field'] = None
            dlg_output['y_fields'] = None
            dlg_output['symbol_color'] = None
        return dlg_output

    def _comma_separated_string_to_list(self, s):
        """
        Utility method to convert a comma-separated string to a list of strings.
        :parameter s: The comma-separated string to convert, as string
        :return: A list of strings
        """
        return [item.strip() for item in s.split(',') if item.strip()]

