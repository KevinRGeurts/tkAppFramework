"""
This module provides the XHTMLParserForTkTextWidget class, which can be used to read XHTML formatted string and
strucure it into data objects that can be used to insert equivalent formatted text into a tkinter Text widget object.

Exported Classes:
    XHTMLParserForTkTextWidget -- This class can be used to read XHTML formatted string and strucure it into
                                  data objects that can be used to insert equivalent formatted text into a
                                  tkinter Text widget object.

Exported Exceptions:
    None    
 
Exported Functions:
    None.
"""

# standard imports
import logging
import tkinter as tk
from tkinter import ttk

# PyPi package imports


# local imports


class XHTMLParserForTkTextWidget(object):
    """
    This class can be used to read XHTML formatted string and strucure it into data objects that can be used
    to insert equivalent formatted text into a tkinter Text widget object.
    """
    def __init__(self, log_level = logging.INFO):
        """
        Initializes the XHTMLParserForTkTextWidget instance.
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        # Create a dictionary that maps XHTML tag onto tkinter Text widget tagName
        #   key = XHTML tab (the opening tag) as string
        #   value = Tuple (tagName, tag options dictionary), as (string, dict)
        #   The tab options dictionary: key = option name (as string), value = option setting
        self._tag_map = {}
        self._populate_tag_map()
        
        self._setup_logging(log_level)

    def _populate_tag_map(self):
        """
        Utility function called to populate self._tag_map attribute, and thus:
            (1) Create a dictionary of XHTML tag to tkinter Text widget tagName
            (2) Create a dictionarhy of configuration options for each tagName to match the formatting implied by the equivalent XHTML tag
        """
        # <h1> to tagName=tag_h1
        options = {}
        options['foreground']='red'
        value = ('tag_h1', options)
        self._tag_map['h1']=value
        return None

    # TODO: This is just a workflow POC at the moment, since it doesn't actually parse the xhtml_string, but just
    # assumes it is an <h1> tag
    def xhtml_string_to_elements(self, xhtml_string):
        """
        Call this method to convert a properly formatted string of XHTML data to elements.
        :param xhtml_string: String containing XHTML data.
        :return: Tuple (tagName list, text element list), as ([string], [string])
        """
        assert(type(xhtml_string)==str)
        tag_list = []
        for key in self._tag_map:
            # ('tag_h1', {'foreground':'red'})
            tag_list.append(self._tag_map[key])
        text_list = []
        element = ('tag_h1', xhtml_string)
        text_list.append(element)
        return (tag_list, text_list)

    def _setup_logging(self, log_level=logging.INFO):
        """
        This method configures logging.
        :param log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        :return: None
        """
        # Create a logger with name 'xhtml_parser_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        logger = logging.getLogger('xhtml_parser_logger')
        # This is the threshold level for the logger itself, before it will pass to any handlers, which can have their own threshold.
        # Should be able to control here what the stream handler receives and thus what ends up going to stderr.
        # Use this key for now:
        #   DEBUG = debug messages sent to this logger will end up on stderr
        #   INFO = info messages sent to this logger will end up on stderr
        logger.setLevel(log_level)
        # Set up this highest level below root logger with a stream handler
        sh = logging.StreamHandler()
        # Set the threshold for the stream handler itself, which will come into play only after the logger threshold is met.
        sh.setLevel(log_level)
        # Add the stream handler to the logger
        logger.addHandler(sh)
            
        return None
