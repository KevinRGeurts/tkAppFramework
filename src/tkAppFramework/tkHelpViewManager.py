"""
This module defines the tkHelpViewManager class. It is a concrete implementation of tkViewManager.
It acts as a Mediator and an Observer, and handles the interactions between the help viewer application's widgets.

Exported Classes:
    tkHelplViewManager -- Concrete implementation of tkViewManager.
                          Acts as a Mediator and an Observer, and handles the interactions between
                          the help viewer application's widgets.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk

# Local imports
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject
from tkAppFramework.xhtml_parser_for_tktextwidget import XHTMLParserForTkTextWidget


class tkHelpViewManager(tkViewManager):
    """
    Concrete implementation of tkViewManager. Acts as Observer, and handles the interactions between help viewer application's widgets.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, most probably a Toplevel window
        """
        tkViewManager.__init__(self, parent)
        
    def _CreateWidgets(self):
        """
        Concrete implementation of tkViewManager._CreateWidgets.
        Sets up and registers the child widgets of the tkHelpViewManager widget.
        :return None:
        """

        self._helptxt_widget = HelpTextWidget(self)
        self.register_subject(self._helptxt_widget, self.handle_helptxt_widget_update)
        self._helptxt_widget.attach(self)
        self._helptxt_widget.grid(column=0, row=0, sticky='NWES') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        return None

    def handle_helptxt_widget_update(self):
        """
        Handle updates from help text widget.
        :return None:
        """
        # Do something as needed.
        return None

    def handle_model_update(self):
        """
        Handler function called when the model notifies the view manager of a change in state.
        :return None:
        """
        (help_content, help_format) = self.getModel().get_help_content()
        self._helptxt_widget.processHelpContent(help_content, help_format)
        return None


class HelpTextWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which allow viewing of help topic content.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        ttk.Labelframe.__init__(self, parent, text="Help Topic Content")
        Subject.__init__(self)

        self._txt_content = tk.Text(self)
        self._txt_content.grid(column=0, row=0, sticky='NWSE') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        # Create a vertical Scrollbar and associate it with _txt_content
        self._scrollbar_vert = ttk.Scrollbar(self, command=self._txt_content.yview)
        self._scrollbar_vert.grid(column=1, row=0, sticky='NWSE')
        self._txt_content['yscrollcommand'] = self._scrollbar_vert.set

        # Create a horizontal Scrollbar and associate it with _txt_content
        self._scrollbar_hor = ttk.Scrollbar(self, command=self._txt_content.xview, orient='horizontal')
        self._scrollbar_hor.grid(column=0, row=1, sticky='NWSE')
        self._txt_content['xscrollcommand'] = self._scrollbar_hor.set
    
    def processHelpContent(self, help_content='', help_format='txt'):
        """
        Method that processes help content and inserts it into the Text widget.
        :parameter help_content: Help content to be processed and inserted, as string
        :parameter help_format: Help content format (either 'txt', or 'xhtml'), as string
        :return: None
        """
        assert(type(help_content)==str)
        assert(type(help_format)==str)
        assert(help_format in ['txt', 'xhtml'])

        # Clear any existing content from the Text widget
        self._txt_content.config(state='normal')
        self._txt_content.delete('1.0', tk.END)

        match help_format:

            case 'txt':
                self._txt_content.insert(tk.INSERT, help_content)

            case 'xhtml':
                # TODO: Process the xhtml content and format it in the Text widget.
                # For now, no processing. Just insert the raw xhtml into the Text widget.
                self._processXHTMLHelpContent(help_content)

        self._txt_content.config(state='disabled')
        
        return None

    def _processXHTMLHelpContent(self, help_content):
        """
        Utility method, called by _ProcessHelpContent(), that processes XHTML help content and inserts it into the Text widget.
        :parameter help_content: Help content to be processed and inserted, as string
        :return: None
        """
        assert(type(help_content)==str)
        parser = XHTMLParserForTkTextWidget()
        (tag_list, text_list) = parser.xhtml_string_to_elements(help_content)
        # Create tkinter Text widget tags
        for tag in tag_list:
            self._txt_content.tag_config(tag[0], tag[1])
        # Insert each item in the text_list, appropriately tagged, into the Text widget
        for item in text_list:
            # item = {tagName, text content}
            begin_index = self._txt_content.index(tk.INSERT)
            self._txt_content.insert(begin_index, item[1])
            end_index = self._txt_content.index(tk.INSERT)
            self._txt_content.tag_add(item[0], begin_index, end_index)
        return None

