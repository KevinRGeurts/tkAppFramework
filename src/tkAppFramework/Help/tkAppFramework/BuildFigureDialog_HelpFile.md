# Build Data Grid Figure Help

This content is generally applicable to the Data Grid Widget's Build Data Grid Figure Dialog, regardless of exactly what application is using it.

## Figure Type Entry:

Type the type of figure to build. Valid values are 'scatter', 'bar', 'box', or 'histogram'. The figure type is case-sensitive.

## X-Axis Field Name Entry:

Type the name of the data grid field to be used for the X-Axis of the figure. The field name is case-sensitive.
If the figure type is 'box' or 'histogram', this entry is not used.

## Y-Axis Field Name(s) Entry:

Type the name(s) of the data grid field(s) to displayed on the Y-Axis of the figure. The field name(s) is/are case-sensitive.
If more than one field name is specified, they should be separated by commas.
If the figure type is 'histogram', only a single field name should be specified.

## Symbol(s) / Color(s) Entry:

- If the figure type is 'scatter', this entry specifies the symbol(s), color(s), and line style(s) to be used for the data points and lines in the figure.
- If the figure type is 'bar', this entry specifies the color(s) to be used for the bars in the figure.
- If the figure type is 'box' or histogram, this entry is not used.

The symbols and colors are case-sensitive. If more than one symbol and/or color is specified, they should be separated by commas.
For the 'scatter' and 'bar' figure types, the number of symbols and/or colors specified should match the number of Y-Axis field names specified.
Valid values of symbols and colors are defined by the matplotlib library. See the matplotlib documentation for details.

## Buttons:

- OK: Clicking this button will (1) create the specified figure, (2) add it to the data grid's list of availalble figures, and (3) close the dialog.
- Cancel: Clicking this button will close the dialog without taking any action.
- Help: Clicking this button will display this help content.

