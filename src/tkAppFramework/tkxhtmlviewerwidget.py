"""
This module defines the tkXHTMLViewerWidget class. It is a tkinter widget that uses a tkinter Text widget to display
formated markdown or HTML content.

Exported Classes:
    tkXHTMLViewerWidget -- It is a tkinter widget that uses a tkinter Text widget to display
                           formated HTML content. It is a Subject in an Observer design pattern,
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
import webbrowser

# Local imports
from tkAppFramework.ObserverPatternBase import Subject
from tkAppFramework.xhtml_parser_for_tktextwidget import XHTMLParserForTkTextWidget, TkWidgetXHTMLParserInterface


class tkXHTMLViewerWidget(ttk.Labelframe, Subject, TkWidgetXHTMLParserInterface):
    """
    Class represents a tkinter label frame, the widget contents of which allow viewing of formatted HTML content.
    Class is also a Subject in Observer design pattern, and provides a TkWidgetXHTMLParserInterface.
    """
    def __init__(self, parent, title='Help Topic Content') -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter title: The text label of the Labelframe, as string
        """
        ttk.Labelframe.__init__(self, parent, text=title)
        Subject.__init__(self)
        TkWidgetXHTMLParserInterface.__init__(self)

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
        self._parser = XHTMLParserForTkTextWidget(self)
    
    def processViewerContent(self, viewer_content='', content_format='txt'):
        """
        Method that processes text or xhtml content and inserts it into the Text widget.
        :parameter viewer_content: Content to be processed and inserted into viewer, as string
        :parameter content_format: Content format (either 'txt', or 'xhtml'), as string
        :return: None
        """
        assert(type(viewer_content)==str)
        assert(type(content_format)==str)
        assert(content_format in ['txt', 'xhtml'])

        # Clear any existing content from the Text widget
        self._txt_content.config(state='normal')
        self._txt_content.delete('1.0', tk.END)

        match content_format:

            case 'txt':
                self._txt_content.insert(tk.INSERT, viewer_content)

            case 'xhtml':
                self._processXHTMLHelpContent(viewer_content)

        self._txt_content.config(state='disabled')
        
        return None

    def _processXHTMLHelpContent(self, viewer_content):
        """
        Utility method, called by processViewerContent(), that processes XHTML help content and inserts it into the Text widget.
        :parameter help_content: Help content to be processed and inserted, as string
        :return: None
        """
        assert(type(viewer_content)==str)
        self._parser.process_xhtml(viewer_content)
        return None

    def onHyperlinkClick(self, event, url):
        """
        Handler called when user clicks on a hyperlink in the Text widget.
        :parameter event: tkinter event that resulted in this handler being called
        :parameter url: The url for the anchor that was clicked, as string
        :return: None
        """
        # Show a message box with the hyperlink url, and ask the user if they want to launch a browser
        # to view the link.
        _title = 'Confirm okay to launch browser'
        _msg = f"Do you wish to launch a browser to display URL: \"{url}\"?"
        response = tkinter.messagebox.askyesno(title=_title, message=_msg, default=tkinter.messagebox.NO)
        if response:
            webbrowser.open(url)
        return None

    def insert_text(self, starting_index='', text=''):
        """
        Method used by XHTML parser to insert text into Text widget.
        :parameter start_index: tkinter Text widget index to start any text insertions, as string
        :parameter text: The text to insert into the Text widget, as string
        :return: tkinter Text widget index at the end of any text insertions, as string
        """
        super().insert_text(starting_index, text)
        self._txt_content.insert(starting_index, text)
        ending_index = self._txt_content.index(tk.INSERT)
        return ending_index

    def tag_text(self, starting_index='', ending_index='', tagName='', link_url=''):
        """
        Method used by XHTML parser to tag text in a Text widget.
        :parameter start_index: tkinter Text widget index of start of text to tag, as string
        :parameter ending_index: tkinter Text widget index of the end of any text to tag, as string
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter link_url: The URL to "bind" to tagName, as string
        :return: None
        """
        super().tag_text(starting_index, ending_index, tagName)
        self._txt_content.tag_add(tagName, starting_index, ending_index)
        if len(link_url) > 0:
            self._txt_content.tag_bind(tagName, '<Button-1>', partial(self.onHyperlinkClick, url=link_url))
        return None

    def config_tag(self, tagName='', options_dict={}):
        """
        Method used by XHTML parser to add and configure options for a tag in tkinter Text widget.
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter options_dict: The dictionary of configuration options for the tag, as dict with key = option_name, value = option_setting
        :return: None
        """
        super().config_tag(tagName, options_dict)
        self._txt_content.tag_config(tagName, options_dict)
        return None

    def get_start_index(self):
        """
        Method used by XHTML parser to get the current insertion index for the tkinter Text widget.
        :return: The current index, as string
        """
        super().get_start_index()
        index = self._txt_content.index(tk.INSERT) 
        return index
