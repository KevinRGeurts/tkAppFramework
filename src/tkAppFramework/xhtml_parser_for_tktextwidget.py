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


class TkWidgetXHTMLParserInterface(object):
    """
    This class defines methods that a tkinter Widget must extend inorder to use a XHTMLParserForTkTextWidget object.
    Extension should be implemented by calling super().<method name> first in the extended method. The implementations
    in this class perform type checking on method parameters using assert(...).
    """
    def insert_text(self, starting_index='', text=''):
        """
        Method used by XHTML parser to insert text into widget.
        :parameter start_index: widget index to start any text insertions, as string
        :parameter text: The text to insert into the widget, as string
        :return: tkinter widget index at the end of any text insertions, as string
        """
        assert(type(starting_index)==str)
        assert(type(text)==str)
        ending_index = ''
        return ending_index

    def tag_text(self, starting_index='', ending_index='', tagName='', link_url=''):
        """
        Method used by XHTML parser to tag text in a widget.
        :parameter start_index: tkinter widget index of start of text to tag, as string
        :parameter ending_index: tkinter widget index of the end of any text to tag, as string
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter link_url: The URL to "bind" to tagName, as string
        :return: None
        """
        assert(type(starting_index)==str)
        assert(type(ending_index)==str)
        assert(type(tagName)==str)
        assert(type(link_url)==str)
        return None

    def config_tag(self, tagName='', options_dict={}):
        """
        Method used by XHTML parser to add and configure options for a tag in tkinter widget.
        :parameter tagName: The tagName with which to tag the text, as string
        :parameter options_dict: The dictionary of configuration options for the tag, as dict with key = option_name, value = option_setting
        :return: None
        """
        assert(type(tagName)==str)
        assert(type(options_dict)==dict)
        return None

    def get_start_index(self):
        """
        Method used by XHTML parser to get the current insertion index for the tkinter widget.
        :return: The current index, as string
        """
        index = ''
        return index


class XHTMLParserForTkTextWidget(object):
    """
    This class can be used to read XHTML formatted string and use a set of call back functions
    to insert equivalent formatted text into a tkinter Text widget object.
    """
    def __init__(self, client = None, log_level = logging.INFO):
        """
        Initializes the XHTMLParserForTkTextWidget instance.
        :parameter client: An object that implements TkWidgetXHTMLParserInterface.
        :parameter log_level: The logging level to set for the logger, e.g., logging.DEBUG, logging.INFO, etc.
        """
        if client is not None:
            assert(isinstance(client, TkWidgetXHTMLParserInterface))
        self._client = client
        
        # Create a dictionary that maps XHTML tag onto tkinter Text widget "base" tagName
        #   key = XHTML tag (the opening tag) as string, without the '<>'
        #   value = Tuple (tagName, tag options dictionary), as (string, dict)
        #   The tag options dictionary: key = option name (as string), value = option setting
        self._tag_map = {}
        self._populate_tag_map()
        # self._tag_id will be used as a suffix to provide a unique name for each tag.
        # This will be increment each time _getTagIDSuffix() method is called.
        self._tag_id=0
        # Create a dictionary that maps TreeElement id's onto starting and ending indices in the Text widget.
        #   key = id(Element), as int
        #   value = (starting_index, ending_index), as (string, string)
        self._elem_insert_indices = {}
        # Create a dictionary that maps a TreeElement's id onto an integer value. This is to be used
        # when an ordered list is encountered in the ElementTree, and it is necessary to prepend
        # a list item number at the front of the text for each list item.
        #   key = id(Element), as int
        #   value = current list item count, as int
        self._elem_ol_counter = {}
        
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
        # Create a font for regular body text
        font_family='Arial'
        font_base_size = 12 # For regular body text, in points
        base_font = tkFont.Font(family=font_family, size=font_base_size, weight='normal')
        # Create a font for code block text
        font_family = 'Courier'
        code_font = tkFont.Font(family=font_family, size=font_base_size, weight='normal')
        # Some metrics that will be used throughout
        base_font_height = base_font.metrics('linespace') # The height of the base font, in pixels
        header_size_step = 4 # The amount by which a header steps up in increments from header 3 to 2 to 1, in points.
        # <body> to tagName=tag_body
        options = {}
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
        # <h2> to tagName=tag_h2
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size+2*header_size_step, weight='bold')
        options['font']= font
        font_height = font.metrics('linespace') # The height of the font, in pixels
        options['spacing3']=0.5*font_height
        value = ('tag_h2', options)
        self._tag_map['h2']=value
        # <h3> to tagName=tag_h3
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size+header_size_step, weight='bold')
        options['font']= font
        font_height = font.metrics('linespace') # The height of the font, in pixels
        options['spacing3']=0.5*font_height
        value = ('tag_h3', options)
        self._tag_map['h3']=value
        # <em> to tagName=tag_em
        options = {}
        font = tkFont.Font(family=font_family, size=font_base_size, weight='bold')
        options['font']= font
        value = ('tag_em', options)
        self._tag_map['em']=value
        # <li> to tagName=tag_li, a list item
        options = {}
        options['font']=base_font
        options['lmargin1']=f"{2*font_base_size}p"
        options['lmargin2']=f"{3*font_base_size}p"
        value = ('tag_li', options)
        self._tag_map['li']=value
        # <a> to tagName=tag_a, a url anchor
        options = {}
        options['foreground']='blue'
        options['underline']=1
        value = ('tag_a', options)
        self._tag_map['a']=value
        # <code> to tagName=tag_code, a code block
        options = {}
        options['font']=code_font
        options['lmargin1']=f"{2*font_base_size}p" # How much to indent first line of text, in points
        options['lmargin2']=f"{2*font_base_size}p" # How much to indent successive lines of text, in points
        value = ('tag_code', options)
        self._tag_map['code']=value

        # TODO: Create more entries in the map, as needed
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
        index = self._client.get_start_index()
        self._process_element_text(element=root, start_index=index)
        # Pass 2: Recurse the ElementTree to tag text in the Text widget, using captured insertion indices
        self._process_element_tags(element=root)
        return None

    def _process_element_text(self, element=None, start_index='', parent=None):
        """
        Utility method called by process_xhtml(...) method to process the text content of one element in the elements tree.
        :parameter element: The element in the element tree to process, as xml.etree.ElementTree.Element
        :parameter start_index: tkinter Text widget index to start any text insertions, as string
        :parameter parent: The element in the element tree that is the parent of the element being processed,
                           as xml.etree.ElementTree.Element
        :return: end_index, as string
                 end_index = tkinter Text widget index at the end of any text insertion
        """
        if element is not None:
            assert(isinstance(element, ET.Element))
        if parent is not None:
            assert(isinstance(parent, ET.Element))
        
        # Get the logger    
        logger = logging.getLogger('xhtml_parser_logger')

        _si = start_index
        _ei = start_index
        # Get the element's 'text', that is, the text of the element itself
        el_txt = element.text
        # Get the element's xhtml tag
        el_tag = element.tag
        if el_tag == 'ol':
            # We are entering an ordered list. We need to initialize and item counter for this list.
            self._elem_ol_counter[id(element)] = 1
        # Insert element's 'text' into the Text widget
        if el_txt is not None:
            if el_tag == 'li' and parent.tag == 'ul':
                # We have an element of an unordered list, and we need to insert a "quirky dot" into the
                # element's text. For now we'll just insert a '*', but later it may be better to get the
                # unicode for a dot.
                el_txt = f"* {el_txt}"
                # We also need to modify the text of the element, so that later when tagging, we have the
                # right text length.
                element.text = el_txt
            if el_tag == 'li' and parent.tag == 'ol':
                # We have an element of an ordered list, and we need to insert a list item number into the
                # element's text. 
                list_item_number = self._elem_ol_counter[id(parent)]
                el_txt = f"({list_item_number}) {el_txt}"
                self._elem_ol_counter[id(parent)] += 1
                # We also need to modify the text of the element, so that later when tagging, we have the
                # right text length.
                element.text = el_txt
            _ei = self._client.insert_text(_si, el_txt)
            logger.debug(f"Inserted element text \'{el_txt}\' from indices {_si} to {_ei}.")
        # Capture the start and end indices for the element's text
        self._elem_insert_indices[id(element)]=(_si, _ei)
        # Iterate through the direct children of element, and proccess them
        for j in range(len(element)):
            _ei = self._process_element_text(element[j], _ei, element)
        # Get any 'tail' text for the element
        el_tail = element.tail
        if el_tail is not None:
            _si = _ei
            # Insert the element's 'tail' text into the Text widget
            _ei = self._client.insert_text(_si, el_tail)
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
        # Possible get the url if element is an anchor (hyperlink)
        el_href = ''
        if el_tag == 'a':
            # Get the actual href
            el_href = element.attrib['href']
        try:
            # Get a tkinter Text widget tagName aand configuration for this element
            (tagName, config_dict) = self.build_tagName(el_tag)
            # Tag the text inserted for this element
            self._client.tag_text(_si, _ei, tagName, el_href)
            logger.debug(f"Tagged text from indices {_si} to {_ei} with {tagName}")
            # Configure the tag
            self._client.config_tag(tagName, config_dict)
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
