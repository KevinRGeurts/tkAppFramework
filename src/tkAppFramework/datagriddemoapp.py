"""
Defines classes for a datagrid demo application, which is also used for unittesting of the datagrid widget and its elements.
"""

# Standard
import logging
import tkinter as tk
from tkinter import ttk
import sysconfig
from math import sqrt

# Local
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject
from tkAppFramework.model import Model
import tkAppFramework.tkApp
from tkAppFramework.tkdatagridwidget import tkDataGridWidget, FieldType, tkDGElementText
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError


class DataGridDemoModel(Model):
    """
    A concrete implementation of Model for the demo datagrid application.
    """
    def __init__(self) -> None:
        super().__init__()
        
    def compute_result(self, base, add_to, multiply_by):
        """
        Compute a result based on the given base, add_to, and multiply_by values. This is just an example of a method
        that the model might have to perform some business logic for the datagrid demo app.
        :param base: A number to be used as the base value in the computation.
        :param add_to: A number to be added to the base value.
        :param multiply_by: A number to multiply the sum of the base and add_to values by.
        :return: The result of (base + add_to) * multiply_by
        """
        return (base + add_to) * multiply_by


class DataGridDemotkViewManager(tkViewManager):
    """
    Provide an implementation of _CreateWidgets(...). Implements handler functions for updates from the model
    and the tkDataGrid widget.
    """
    def _CreateWidgets(self):
        """
        Create the demo widget, register 
        :return None:
        """
        field_configurations = [('Base',FieldType.TEXT,'editable'),
                                ('Add 2 to',FieldType.BOOL,'editable'),
                                ('Multiply by',FieldType.LIST,'editable'),
                                ('Result',FieldType.TEXT,'read_only')]
        self._dg = tkDataGridWidget(self, title='Demo Data Grid', fields_config=field_configurations, num_records=5,
                                    log_level = logging.DEBUG)
        # Attach self as an observer of the subject demo widget
        self._dg.attach(self)
        # Register a handler function for updates from the subject datagrid widget
        self.register_subject(self._dg, self.handle_datagrid_widget_update)
        # Place datagrid widget in grid and set weights for stretching the column and row in the grid
        # so that the demo widget resizes correctly.
        self._dg.grid(column=0, row=0, sticky='NWES')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Initialize the datagrid.
        self._initialize_data_grid()
        return None

    def _initialize_data_grid(self):
        """
        Initialize the datagrid with values for the records.
        :return None:
        """
        for i in range(self._dg.num_records):
            # Initialze the 'Multiply by' field for each record.
            self._dg.set_grid_element_list_choices('Multiply by', i, ('1.0', '2.0', '3.0', '4.0'))
            self._dg.set_grid_element_default_value('Multiply by', i, '2.0')
            self._dg.set_grid_element_value('Multiply by', i, '2.0')
            # Initialize the 'Base' field for each record.
            self._dg.set_grid_element_value('Base', i, str(i))
        return None
    
    def handle_model_update(self):
        """
        Handle updates from the model.
        :return None:
        """
        print(f"DataGridDemotkViewManager received a model update notification.")
        return None
    
    def handle_datagrid_widget_update(self):
        """
        Handle updates from the datagrid widget, by running the updated record through the model to get a new result,
        and then updating the 'Result' field of the record with the new result from the model.
        :return None:
        """
        # Determine the field name and record index of the modified element.
        (field_name, record_index) = self._dg.get_modified_grid_element_location()
        modified_value = self._dg.get_grid_element_value(field_name, record_index)
        print(f"View manager informed of data grid widget element update from grid element at (field name = {field_name}, record index = {record_index}). Element''s value is {modified_value}.")
        # Raise an error for invalid entry, if the modified element's value "invalid" as text string.
        # This is just to test the handling of invalid entries.
        if modified_value == 'invalid':
            msg = f"Invalid entry of 'invalid' in data grid element at (field name = {field_name}, record index = {record_index})."
            raise tkDGElementTextInvalidEntryError(msg)
        try:
            # Get the current Result value for the record.
            current_result = float(self._dg.get_grid_element_value('Result', record_index))
        except:
            # Arbitrary value to use for current_result if there is an error getting the current result, such as if the current result is not a valid float.
            # This will (likely) ensure that the first new result from the model will be different from the current result,
            # so that the 'Result' field of the record will be updated with the new result from the model.
            current_result = -99.99
        try:
            # Get the values required by the model for a computation out of the record's fields
            base_val = float(self._dg.get_grid_element_value('Base', record_index))
            add_to_val = 2.0 if self._dg.get_grid_element_value('Add 2 to', record_index) == 1.0 else 0.0
            multiply_by_val = float(self._dg.get_grid_element_value('Multiply by', record_index))
            # Ask the model to compute a result based on the values from the record's fields.
            result = self.getModel().compute_result(base_val, add_to_val, multiply_by_val)
            # Update the 'Result' field of the record with the result from the model, IFF it is different from the current result
            # This prevents an infinite loop of updates.
            if result != current_result:
                self._dg.set_grid_element_value('Result', record_index, str(result))
        except:
            self._dg.clear_grid_element_value('Result', record_index)
        return None


class DataGridDemotkApp(tkAppFramework.tkApp.tkApp):
    """
    Provide implementations of _createViewManager() and _createModel() factory methods.
    """
    def __init__(self, parent):
        help_file_path = sysconfig.get_path('data') + '\\Help\\tkAppFramework\\HelpFile.txt'
        info = tkAppFramework.tkApp.AppAboutInfo(name='DataGrid Demo Application', version='0.1', copyright='2026', author='John Q. Public',
                                                 license='MIT License', source='GitHub', help_file=help_file_path)
        super().__init__(parent, title="DataGrid Demo Application", app_info=info, file_types=[('Text file', '*.txt')])

    def _createViewManager(self):
        """
        Concrete Implementation, which returns a DemotkViewManager instance.
        :return: tkViewManager instance that will be the app's view manager
        """
        return DataGridDemotkViewManager(self)

    def _createModel(self):
        """
        Concrete Implementation, which returns a DemoModel().
        :return: DemoModel instance that will be the app's model
        """
        return DataGridDemoModel()


