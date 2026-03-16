"""
This module provides the XHTMLParserForTkTextWidget class, which can be used to read XHTML formatted string and
strucure it into data objects that can be used to insert equivalent formatted text into a tkinter Text widget object.

Exported Classes:
    XHTMLParserForTkTextWidget -- This class can be used to read XHTML formatted string and use a set of call back functions
                                  to insert equivalent formatted text into a tkinter Text widget object.

Exported Exceptions:
    None    
 
Exported Functions:
    None.
"""

# standard imports
import logging
import xml.etree.ElementTree as ET
import tkinter as tk
import tkinter.font as tkFont

# local imports
from tkAppFramework.exceptions import NoWidgetTagConfigurationAvailableForXHTMLTag


class XHTMLParserForTkTextWidget(object):
    """
    This class can be used to read XHTML formatted string and use a set of call back functions
    to insert equivalent formatted text into a tkinter Text widget object.
    """
    def __init__(self, insert_txt_cb = None, tag_txt_cb = None, config_tag_cb = None, start_index_cb = None,
                 log_level = logging.INFO):
        """
        Initializes the XHTMLParserForTkTextWidget instance.
        :parameter insert_txt_cb: Call back function for inserting text into a tkinter Text wdiget object, as callable
            Signature: ending_index = func(starting_index, text), as str = func(str, str)
        :parameter tag_txt_cb: Call back function for tagging text in a tkinter Text wdiget object, as callable
            Signature: func(starting_index, ending_index, tagName), as None = func(str, str, str)
        :parameter config_tag_cb: Call back function for creating and configuring a tag in a tkinter Text wdiget object, as callable
            Signature: func(tagName, options_dict), as None = func(str, dict)
        :parameter start_index_cb: Call back function for getting the current insertion index for a tkinter Text wdiget object, as callable
            Signature: current_index = func(), as str = func()
        :parameter log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        if insert_txt_cb is not None:
            assert(callable(insert_txt_cb))
        if tag_txt_cb is not None:
            assert(callable(tag_txt_cb))
        if config_tag_cb is not None:
            assert(callable(config_tag_cb))
        if start_index_cb is not None:
            assert(callable(start_index_cb))
        self._insert_txt_cb = insert_txt_cb
        self._tag_txt_cb = tag_txt_cb
        self._config_tag_cb = config_tag_cb
        self._start_index_cb = start_index_cb
        
        # Create a dictionary that maps XHTML tag onto tkinter Text widget "base" tagName
        #   key = XHTML tag (the opening tag) as string, without the '<>'
        #   value = Tuple (tagName, tag options dictionary), as (string, dict)
        #   The tag options dictionary: key = option name (as string), value = option setting
        self._tag_map = {}
        self._populate_tag_map()
        # self._tag_id will be used as a suffix to provide a unique name for each tag.
        # This will be increment each time _getTagIDSuffix() method is called.
        self._tag_id=0
        # Create a dictionary that maps TreeElement id's onto starting and ending indices in teh Text widget.
        #   key = id(Element), as int
        #   value = (starting_index, ending_index), as (string, string)
        self._elem_insert_indices = {}
        
        self._setup_logging(log_level)

    def _getTagIdSuffix(self):
        """
        Utility method called by build_tagName(...) method to get the current unique tag id suffix.
        :return: Tag ID unique suffix, as string
        """
        result = self._tag_id
        self._tag_id += 1
        return str(result)

    def build_tagName(self, xhtml_tag=''):
        """
        Build a tkinter Text widget tagName based on the xhtml_tag and the unique tag ID suffix.
        :parameter xhtml_tag: An xhtml tag, like 'h1' or 'em'. Do NOT include the '<>'. As string.
        :return: Tuple (unique_tagName, config_dict):
                 unique_tagName = A unique tkinter Text widget tag name, of the form tag_{xhtml_tag}_{X}, where {X} is a unique integer
                                  converted to a string. As string.
                config_dict = Dictionary of configuration options for the tag, as dict
        """
        assert(type(xhtml_tag)==str)
        # Look up tkinter Text widget tag "base name" for this element
        try:
            (base_tagName, options_dict) = self._tag_map[xhtml_tag]
        except KeyError:
            raise NoWidgetTagConfigurationAvailableForXHTMLTag
        tagName = base_tagName + '_' + self._getTagIdSuffix()
        return (tagName, options_dict)
        
    def _populate_tag_map(self):
        """
        Utility function called to populate self._tag_map attribute, thus:
            (1) Create a dictionary of XHTML tag to tkinter Text widget tagName
            (2) Create a dictionarhy of configuration options for each tagName to match the formatting implied by the equivalent XHTML tag
        """
        font_family='Helvetica'
        font_base_size = 12 # For regular body text, in points
        base_font = tkFont.Font(family=font_family, size=font_base_size, weight='normal')
        base_font_height = base_font.metrics('linespace') # The height of the font, in pixels
        header_size_step = 4 # The amount by which a header steps up in increments from header 3 to 2 to 1, in points.
        # TODO: These are only prototype configurations for testing. Many need to be configures with a font.
        # <body> to tagName=tag_body
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size, weight='normal')
        options['font']=base_font
        options['lmargin1']=f"{font_base_size}p" # How much to indent first line of text, in points
        options['lmargin2']=f"{font_base_size}p" # How much to indent successive lines of text, in points
        options['rmargin']=f"{font_base_size}p" # Size of right margin for text, in points
        options['spacing2']=0.25*base_font_height # Extra space between lines of wrapped text, in pixels
        options['spacing3']=0.25*base_font_height # Extra space between lines of unwrapped text, in pixels
        options['wrap']=tk.WORD
        value = ('tag_body', options)
        self._tag_map['body']=value
        # <p> to tagName=tag_p
        options = {}
        options['spacing3']=0.5*base_font_height
        value = ('tag_p', options)
        self._tag_map['p']=value
        # <h1> to tagName=tag_h1
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size+3*header_size_step, weight='bold')
        options['font']= font
        font_height = font.metrics('linespace') # The height of the font, in pixels
        options['spacing3']=0.5*font_height
        value = ('tag_h1', options)
        self._tag_map['h1']=value
        # <h1> to tagName=tag_h2
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size+2*header_size_step, weight='bold')
        options['font']= font
        font_height = font.metrics('linespace') # The height of the font, in pixels
        options['spacing3']=0.5*font_height
        value = ('tag_h2', options)
        self._tag_map['h2']=value
        # <em> to tagName=tag_em
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size, weight='bold')
        options['font']= font
        value = ('tag_em', options)
        self._tag_map['em']=value
        # <li> to tagName=tag_li, a list item
        # TODO: Work out how to create bullets. This probably will need to be handled by inserting a bullet into the text
        # in Pass 1 through the ElementTree.
        options = {}
        options['font']=base_font
        options['lmargin1']=f"{2*font_base_size}p"
        options['lmargin2']=f"{4*font_base_size}p"
        value = ('tag_li', options)
        self._tag_map['li']=value
        # <a> to tagName=tag_a, a url anchor
        # TODO: Work out how to create bindings while parsing the Element tree in Pass 2.
        options = {}
        options['foreground']='blue'
        value = ('tag_a', options)
        self._tag_map['a']=value

        # TODO: Create more entries in the map
        return None

    def _xhtml_string_to_elements_tree(self, xhtml_string=''):
        """
        Utility method called by process_xhtml(...) method to convert a properly formatted string of XHTML data to a tree or elements
        :param xhtml_string: String containing XHTML data.
        :return: element tree
        """
        assert(type(xhtml_string)==str)
        root = ET.fromstring(xhtml_string)
        return root

    def process_xhtml(self, xhtml_string=''):
        """
        Process all elements in the elements tree, and use call backs to insert and tag text in a tkinter Text widget.
        :param xhtml_string: String containing XHTML data.
        :return: None
        """
        assert(type(xhtml_string)==str)
        # Clear the existing dictionary of element insertion indices
        self._elem_insert_indices.clear()
        # Create an ElementTree representing the XHTML string
        root = self._xhtml_string_to_elements_tree(xhtml_string)
        # Pass 1: Recurse the ElementTree to insert text into the Text widget, and to capture insertion indices.
        index = self._start_index_cb()
        self._process_element_text(element=root, start_index=index)
        # Pass 2: Recurse the ElementTree to tag text in the Text widget, using captured insertion indices
        self._process_element_tags(element=root)
        return None

    def _process_element_text(self, element=None, start_index=''):
        """
        Utility method called by process_xhtml(...) method to process the text content of one element in the elements tree.
        :parameter element: The element in the element tree to process, as xml.etree.ElementTree.Element
        :parameter start_index: tkinter Text widget index to start any text insertions, as string
        :return: end_index, as string
                 end_index = tkinter Text widget index at the end of any text insertion
        """
        logger = logging.getLogger('xhtml_parser_logger')

        _si = start_index
        _ei = start_index
        # Get the element's 'text', that is, the text of the element itself
        el_txt = element.text
        # Insert element's 'text' into the Text widget
        if el_txt is not None:
            _ei = self._insert_txt_cb(_si, el_txt)
            logger.debug(f"Inserted element text \'{el_txt}\' from indices {_si} to {_ei}.")
        # Capture the start and end indices for the element's text
        self._elem_insert_indices[id(element)]=(_si, _ei)
        # Iterate through the direct children of element, and proccess them
        for j in range(len(element)):
            _ei = self._process_element_text(element[j], _ei)
        # Get any 'tail' text for the element
        el_tail = element.tail
        if el_tail is not None:
            _si = _ei
            # Insert the element's 'tail' text into the Text widget
            _ei = self._insert_txt_cb(_si, el_tail)
            logger.debug(f"Inserted element tail text \'{el_tail}\' from indices {_si} to {_ei}.")
        return _ei

    def _process_element_tags(self, element=None):
        """
        Utility method called by process_xhtml(...) method to process the tag of one element in the elements tree.
        :parameter element: The element in the element tree to process, as xml.etree.ElementTree.Element
        :return: None
        """
        logger = logging.getLogger('xhtml_parser_logger')

        # Look up the element's text's indices in the Text widget
        (_si, _ei) = self._elem_insert_indices[id(element)] 
        # Get the element's 'inner text', that is, the text of the element itself and any child elements
        intxt = "".join(element.itertext())
        l_intext = len(intxt)
        # "Calculate" the ending index for tagging by "adding" the length of the element's 'inner text'
        # to the starting index.
        _ei = f"{_si} +{l_intext}c"
        # Get the element's tag
        el_tag = element.tag
        try:
            # Get a tkinter Text widget tagName aand configuration for this element
            (tagName, config_dict) = self.build_tagName(el_tag)
            # Tag the text inserted for this element
            self._tag_txt_cb(_si, _ei, tagName)
            logger.debug(f"Tagged text from indices {_si} to {_ei} with {tagName}")
            # Configure the tag
            self._config_tag_cb(tagName, config_dict)
        except NoWidgetTagConfigurationAvailableForXHTMLTag:
            logger.debug(f"Parser ignored XHTML tag <{el_tag}>.")
        # Iterate through the direct children of element, and proccess them
        for j in range(len(element)):
            self._process_element_tags(element[j])
        return None

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
