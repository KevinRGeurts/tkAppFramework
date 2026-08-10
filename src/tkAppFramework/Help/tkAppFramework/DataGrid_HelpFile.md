# Data Grid Help

This content is generally applicable to the Data Grid Widget, regardless of exactly what application is using it.

## Understanding the colors of grid cells:

- White: The cell value can be changed by the user. Typically this is a cell where you should enter an input value.
- Blue (Cyan): The cell value cannot be changed by the user. Typically this cell displays the results of a computation.
- Green: The current cell value is a default value. If it is changed by the user, the cell color will change to white. The user can select the cell and click F3 key to restore the default value.
- Grey: The field header cells with the names of grid fields are colored grey.

## Moving around in the grid:

- The currently selected cell in the grid is shown with a red border.
- Grid cells can be selected by clicking on them with the left mouse button.
- The selected cell can be changed by moving around the grid with the arrow keys.
- The tab key will move the selected cell in a pre-defined order. Typically this order is to move down the current column and then over to the next column to the right.
- The enter key will enter a new value into the currently selected grid cell without moving from that cell.
- Hovering over a grid cell with the mouse pointer will display a tooltip with the cell's value and default value.

## Changing the units of a field in the grid:

If a field in the grid shows a unit of measurement in the field's header, like 'Length (m)', the user can change the unit of measurement
by selecting that field's header cell and double-clicking the left mouse button. This will launch a dialog where the user can
choose a diffent unit of measurement for the field. When the dialog is okayed, the record values for that field will be updated
to the new unit of measurement.

## Using the grid's context menu:

Clicking the right mouse button when any grid cell is selected will display a "contextual" menu. The available choices on the menu depend on the selected cell.
The available choices also depend on abilities that are granted to the user by the application. For example, in a typical
application, it would not make sense for the user to be able to delete a field from the data grid, but it would make
sense for them to be able to delete a record.

- Delete | Column: Delete the selected element's column, it is is a data grid record
- Delete | Row: Delete the selected element's row, if it is a data grid record
- Edit | Copy: Copy text content selected within the cell to the clipboard
- Edit | Paste: Paste content from the clipboard into the cell's text content at the insertion point
- Export | CSV: Save the values in the grid's cells to a Comma Separated Value file. Not currently implemented.
- Export | JSON: Save the values in the grid's cells to a Java Scipt Object Notation file. Not currently implemented. 
- Export | PostScript: Create a printable Encapsulated PostScript file of the grid
- Help on Data Grid: Display this help content
- Insert | Column Left: Insert a column to the left of the selected element's column, if it is a data grid record
- Insert | Column Right: Insert a column to the right of the selected element's column, if it is a data grid record
- Insert | Row Above: Insert a row above the selected element's row, if it is a data grid record
- Insert | Row Below: Insert a row below the selected element's row, if it is a data grid record
- Restore Default Value: Restore the default value for the selected cell, if it has a default value, and is not read-only
- Show Graph | {graph name}: Show the graph with the given name, based on data in the data grid. Return to the data grid by pressing the escape key.
- Unit Change: Launch the unit of measurement selection dialog for the selected element's field, if the field has units
