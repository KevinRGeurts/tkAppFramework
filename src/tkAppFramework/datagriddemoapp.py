"""
Defines classes for a data grid demo application.

Exported Classes:
    DemoUoMSystem -- A demo units of measurement system class, used in the data grid demo application to demonstrate how a
                     UoMSysAdapter might be implemented for a specific unit system implementation.
    DemoUoMSysAdapter -- A concrete implementation of UoMSysAdapter for the data grid demo application.
    DataGridDemoModel -- A concrete implementation of Model for the demo data grid application.
    DataGridDemotkViewManager -- A concrete implementation of tkViewManager for the demo data grid application.
                                 Illustrates how to:
                                 (1) Create a tkDataGridWidget with field configurations, user abilities, and a UoMSysAdapter.
                                 (2) Initialize the tkDataGridWidget with values for the records.
                                 (3) Handle update notifications from the tkDataGridWidget widget, by running the updated record through the model to get a new result,
                                     and then displaying that result in the grid.
    DataGridDemotkApp -- A concrete implementation of tkApp for the demo data grid application.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""

# Standard
import logging
import sysconfig
from functools import partial

# Local
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.model import Model
import tkAppFramework.tkApp
from tkAppFramework.tkdatagridwidget import tkDataGridWidget, FieldType, FieldConfiguration, UpdateHint, DataGridAddRecordUpdateHint 
from tkAppFramework.tkdatagridwidget import DataGridDeleteRecordUpdateHint, DataGridUserAbilities, DataGridChangedRecordUpdateHint 
from tkAppFramework.exceptions import tkDGElementTextInvalidEntryError
from tkAppFramework.tkdgelementtextvalidators import tkDGTextElemValidator
from tkAppFramework.uomsysadapter import UoMSysAdapter
from tkAppFramework.datagridfigurewidget import ScatterPlotFieldsFigureTemplate, BarPlotFieldsFigureTemplate


class DemoUoMSystem:
    """
    A demo units of measurement system class, used in the datagrid demo application to demonstrate how a
    UoMSysAdapter might be implemented for a specific unit system and how it might be used in the
    datagrid containing application.
    """
    def get_units_for_group(self, group_id):
        unit_list = []
        match group_id:
            case 'gid_length':
                unit_list = ['uid_meter', 'uid_foot', 'uid_inch']
        return unit_list

    def get_base_unit(self, group_id):
        base_unit_id = None
        match group_id:
            case 'gid_length':
                base_unit_id = 'uid_meter'
        return base_unit_id

    def get_unit_names(self, unit_id):
        name_list = []
        match unit_id:
            case 'uid_meter':
                name_list = ['m', 'meter', 'metre']
            case 'uid_foot':
                name_list = ['ft', 'foot']
            case 'uid_inch':
                name_list = ['in', 'inch']
        return name_list

    def unit_conversion(self, value, from_unit, to_unit):
        ret_val = 0.0
        # First, convert value to base units. In this example, we will use meter as the base unit for length.
        match from_unit:
            case 'uid_meter':
                ret_val = value
            case 'uid_foot':
                ret_val = value * 0.3048
            case 'uid_inch':
                ret_val = value * 0.3048 / 12.0
        # Second, convert value from base units to desired units.
        match to_unit:
            case 'uid_meter':
                ret_val = ret_val
            case 'uid_foot':
                ret_val = ret_val / 0.3048
            case 'uid_inch':
                ret_val = ret_val / 0.3048 * 12.0
        return ret_val


class DemoUoMSysAdapter(UoMSysAdapter):
    """
    A concrete implementation of UoMSysAdapter for the datagrid demo application.
    This is just an example of how a UoMSysAdapter might be implemented for a specific unit system,
    and how it might be used in the datagrid demo application.
    """
    def __init__(self):
        uom_sys = DemoUoMSystem()
        super().__init__(unit_sys=uom_sys)

    def get_unit_ids_of_unit_group(self, unit_group_id):
        """
        Get the unit IDs of the units in the unit group specified by unit_group_id.
        :param unit_group_id: The ID of the unit group to get the unit IDs of, as Any
        :return: A list of unit IDs of the units in the specified unit group, as [Any]
        """
        uid_list = self._unit_sys.get_units_for_group(unit_group_id)
        return uid_list

    def get_unit_names_for_unit(self, unit_id):
        """
        Get the unit names (synonyms) of the unit specified by unit_id.
        :param unit_id: The ID of the unit to get the synonyms for, as Any
        :return: A list of synonyms of the unit with the specified unit ID, as [strings]
        """
        name_list = self._unit_sys.get_unit_names(unit_id)
        return name_list

    def convert(self, from_unit_id, to_unit_id, value):
        """
        Convert value from the unit specified by from_unit_id to the unit specified by to_unit_id.
        :parameter from_unit_id: The ID of the unit to convert from, as Any
        :parameter to_unit_id: The ID of the unit to convert to, as UnitID Any
        :parameter value: The value to convert, as float.
        :return: The converted value, as float. 
        """
        ret_val = self._unit_sys.unit_conversion(value, from_unit_id, to_unit_id)
        return ret_val

    def get_base_unit_id_for_unit_group(self, unit_group_id):
        """
        Get the unit ID of the "base" unit in the unit group specified by unit_group_id.
        Note: The "base" unit is uniquely defined by paticular Units of Measurement System (UoMSys)
              for each unit group. Collectively for all unit groups, base units are the set of units
              used "internally" by the application/model so that calculations are done consistently and
              correctly. 
        :param unit_group_id: The ID of the unit group to get the base unit ID of, as Any
        :return: The base unit ID of the specified unit group, as [Any]
        """
        ret_val = self._unit_sys.get_base_unit(unit_group_id)
        return ret_val


class DataGridDemoModel(Model):
    """
    A concrete implementation of Model for the demo datagrid application.
    """
    def __init__(self) -> None:
        super().__init__()
        
    def compute_result(self, base, multiply_by):
        """
        Compute a result based on the given base and multiply_by values. This is just an example of a method
        that the model might have to perform some business logic for the datagrid demo app.
        :param base: A number to be used as the base value in the computation.
        :param multiply_by: A number to multiply the sum of the base and add_to values by.
        :return: The result of base * multiply_by
        """
        return (base * multiply_by)


class DataGridDemotkViewManager(tkViewManager):
    """
    Provides an implementation of _CreateWidgets(...). Implements handler functions for updates from the model
    and the tkDataGrid widget.
    """
    def _CreateWidgets(self):
        """
        Create and set geometry for the datagrid widget, set up self as an observer of the datagrid,
        and intialize the elements of the data grid. 
        :return None:
        """
        field_configurations = [FieldConfiguration('Record Index', FieldType.TEXT, 'read_only', None, None, None, ''),
                                FieldConfiguration('Compute Result', FieldType.BOOL, 'editable', None, None, None, None),
                                FieldConfiguration('Base', FieldType.NUMBER, 'editable',
                                                   partial(tkDGTextElemValidator.validate_entry_is_float, min_value=0, max_value=None),
                                                   'gid_length', 'uid_meter', 'm'),
                                FieldConfiguration('Multiply by', FieldType.LIST, 'editable', None, None, None, ''),
                                FieldConfiguration('Result', FieldType.NUMBER, 'read_only', None, 'gid_length', 'uid_meter', 'm'),
                                FieldConfiguration('Comment', FieldType.TEXT, 'editable',
                                                   partial(tkDGTextElemValidator.validate_entry_is_string, min_length=0, max_length=15),
                                                   None, None, '')]
        _user_abilities = DataGridUserAbilities(can_insert_field=False, can_delete_field=False, can_insert_record=True,
                                               can_delete_record=True)
        self._dg = tkDataGridWidget(self, title='Demo Data Grid', fields_config=field_configurations, num_records=5,
                                    log_level = logging.INFO, uom_adapter=DemoUoMSysAdapter(),
                                    user_abilities=_user_abilities)
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
            self._initialize_one_record(i)
        # Create scatter plot figure template
        ft = ScatterPlotFieldsFigureTemplate(x_label='Base', y_label='Y-Value', x_field='Base',
                                         y_fields=['Result'], symbols=['bo-'])
        self._dg.register_figure_template('Scatter: Result vs Base', ft)
        # Create bar plot figure template
        ft = BarPlotFieldsFigureTemplate(x_label='Record Index', y_label='Y-Value', x_field='Record Index',
                                             y_fields=['Base', 'Result'], colors=['b', 'r'])
        self._dg.register_figure_template('Bar: Base and Result vs Record Index', ft)
        return None

    def _initialize_one_record(self, index):
        """
        Initialize the index-th record of the data grid, starting at 0.
        :parameter index: The index of the data grid record to initialize, as int
        :return: None
        """
        # Initialize the "Record Index" field
        self._dg.set_grid_element_value('Record Index', index, str(index))
        # Initialize the "Compute Result" field
        self._dg.set_grid_element_value('Compute Result', index, True)
        # Initialze the 'Multiply by' field
        self._dg.set_grid_element_list_choices('Multiply by', index, ('1.0', '2.0', '3.0', '4.0'))
        self._dg.set_grid_element_default_value('Multiply by', index, '2.0')
        self._dg.set_grid_element_value('Multiply by', index, '2.0')
        # Initialize the 'Base' field
        self._dg.set_grid_element_value('Base', index, index)
        self._dg.set_grid_element_default_value('Base', index, index)
        # Initialize the 'Comment' field
        self._dg.set_grid_element_value('Comment', index, 'No comment')
        self._dg.set_grid_element_default_value('Comment', index, 'No comment')
        return None
    
    def handle_model_update(self):
        """
        Handle updates from the model. None needed, since the model doesn't retain any data.
        :return None:
        """
        print(f"DataGridDemotkViewManager received a model update notification.")
        return None
    
    def handle_datagrid_widget_update(self, hints=None):
        """
        Handle updates from the datagrid widget, by running the updated record through the model to get a new result,
        and then updating the 'Result' field of the record with the new result from the model.
        :parameter hints: List of optional hints providing context for datagrid updates, as [UpdateHint]
        :return None:
        """
        # Handle any update hints
        if hints is not None:
            assert(isinstance(hints, list))
            for hint in hints:
                assert(isinstance(hint, UpdateHint))
                if isinstance(hint, DataGridAddRecordUpdateHint):
                    # A new record has been added to the data grid, and needs to be initialized.
                    new_rec_idx = hint.new_record_index
                    for i in range(self._dg.num_records):
                        if i == new_rec_idx:
                            self._initialize_one_record(i)
                        else:
                            # This is a previously existing record, that needs its 'Record Index' field updated
                            self._dg.set_grid_element_value('Record Index', i, str(i))
                elif isinstance(hint, DataGridDeleteRecordUpdateHint):
                    # An existing record has been deleted from the data grid.
                    # Nothing needs to be done in this case, because the model does not retain a list of records.
                    pass
                elif isinstance(hint, DataGridChangedRecordUpdateHint):
                    # Determine the field name and record index of the modified element.
                    field_name = hint.changed_record_field
                    record_index = hint.changed_record_index
                    if record_index > -1:
                        # The update is for a record element and not for a field header element, and is thus a value change.
                        modified_value = self._dg.get_grid_element_value(field_name, record_index)
                        # print(f"View manager informed of data grid widget element update from grid element at (field name = {field_name}, record index = {record_index}). Element\'s value is {modified_value}.")
                        # Raise an error for invalid entry, if the modified element's value is exactly 9.9999e99 as float.
                        # This is just to test the handling of invalid entries that can only be recognized as invalid by the data grid
                        # widget's client.
                        if modified_value == 9.999e99:
                            msg = f"Invalid entry of 9.999e99 in data grid element at (field name = {field_name}, record index = {record_index})."
                            raise tkDGElementTextInvalidEntryError(msg)
                        # Get the current Result value for the record.
                        current_result = self._dg.get_grid_element_value('Result', record_index)
                        try:
                            should_compute = self._dg.get_grid_element_value('Compute Result', record_index)
                            if should_compute:
                                # Get the values required by the model for a computation out of the record's fields
                                base_val = self._dg.get_grid_element_value('Base', record_index)
                                multiply_by_val = float(self._dg.get_grid_element_value('Multiply by', record_index))
                                # Ask the model to compute a result based on the values from the record's fields.
                                # This result is in base units (meters).
                                result = self.getModel().compute_result(base_val, multiply_by_val)
                                # Update the 'Result' field of the record with the result from the model, IFF it is different from the current result.
                                # This prevents an infinite loop of updates.
                                if result != current_result:
                                    self._dg.set_grid_element_value('Result', record_index, result)
                            else:
                                self._dg.clear_grid_element_value('Result', record_index)
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
