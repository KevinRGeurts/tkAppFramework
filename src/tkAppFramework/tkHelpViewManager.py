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
import logging

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

        # Create an XHTML parser object
        self._parser = XHTMLParserForTkTextWidget(insert_txt_cb = self._insert_text, tag_txt_cb = self._tag_text,
                                                  config_tag_cb = self._config_tag, start_index_cb = self._get_start_index,
                                                  log_level = logging.DEBUG)
    
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
                self._processXHTMLHelpContent(help_content)

        self._txt_content.config(state='disabled')
        
        return None

    def _processXHTMLHelpContent(self, help_content):
        """
        Utility method, called by processHelpContent(), that processes XHTML help content and inserts it into the Text widget.
        :parameter help_content: Help content to be processed and inserted, as string
        :return: None
        """
        assert(type(help_content)==str)
        self._parser.process_xhtml(help_content)
        return None

    def _insert_text(self, starting_index='', text=''):
        """
        Call back method used by XHTML parser to insert text into Text widget.
        :parameter start_index: tkinter Text widget index to start any text insertions, as string
        :parameter text: The text to insert into the Text widget, as string
        :return: tkinter Text widget index at the end of any text insertions, as string
        """
        assert(type(starting_index)==str)
        assert(type(text)==str)
        self._txt_content.insert(starting_index, text)
        ending_index = self._txt_content.index(tk.INSERT)
        return ending_index

    def _tag_text(self, starting_index='', ending_index='', tagName=''):
        """
        Call back method used by XHTML parser to tag text in a Text widget.
        :parameter start_index: tkinter Text widget index of start of text to tag, as string
        :parameter ending_index: tkinter Text widget index of the end of any text to tag, as string
        :parameter tagName: The tagName with which to tag the text, as string
        :return: None
        """
        assert(type(starting_index)==str)
        assert(type(ending_index)==str)
        assert(type(tagName)==str)
        self._txt_content.tag_add(tagName, starting_index, ending_index)
        return None

    def _config_tag(self, tagName='', options_dict={}):
        """
        Call back method used by XHTML parser to add and configure options for a tag in tkinter Text widget.
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter options_dict: The dictionary of configuration options for the tag, as dict with key = option_name, value = option_setting
        :return: None
        """
        assert(type(tagName)==str)
        assert(type(options_dict)==dict)
        self._txt_content.tag_config(tagName, options_dict)
        return None

    def _get_start_index(self):
        """
        Call back method used by XHTML parser to get the current insertion index for the tkinter Text widget.
        :return: The current index, as string
        """
        index = self._txt_content.index(tk.INSERT) 
        return index