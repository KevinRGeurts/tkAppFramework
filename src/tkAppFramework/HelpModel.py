"""
This module provides the HelpModel class, which represents the "business logic" of an application for viewing help

Exported Classes:
    HelpModel -- This class represents the help content, and is a Model in the MVC pattern.

Exported Exceptions:
    None    
 
Exported Functions:
    None.
"""

# standard imports

# PyPi package imports
from markdown import markdown
from justhtml import JustHTML

# local imports
from tkAppFramework.model import Model


class HelpModel(Model):
    """
    This class represents the "business logic" of help content, and is a Model in the MVC pattern.
        _help_file: Path to the help file to be opened and displayed initially, string
    """
    def __init__(self, help_file='', help_format='txt') -> None:
        """
        :parameter help_file: Path to the help file to be opened and displayed initially, string
        :parameter help_format: Help file format ('txt', 'xhtml', or 'md), string
        """
        super().__init__()
        self._help_file = ''
        self._help_format = ''
        self._txt_content = ''
        self._xhtml_content = ''
        self._md_content = ''
        self.set_help_file(help_file, help_format)

    def get_help_file(self):
        return (self._help_file, self._help_format)

    def set_help_file(self, help_file, help_format):
        assert(type(help_file)==str)
        assert(type(help_format)==str)
        assert(help_format in ['txt', 'xhtml', 'md'])
        self._help_file = help_file
        self._help_format = help_format
        # Open help file and read it's content.
        if len(self._help_file)>0:
            with open(self._help_file, mode='r', encoding="utf-8") as f:
                    self.readModelFromFile(f, self._help_format)
        self.notify()

    def get_help_content(self):
        """
        Returns help content and help content format. Returns xhtml content preferentially, if any is present. Otherwise
        returns txt content.
        :return: Tuple (help content, help content format), as (string, string)
        """
        if len(self._xhtml_content)>0:
            return (self._xhtml_content, 'xhtml')
        else:
            return (self._txt_content, 'txt')

    def readModelFromFile(self, file, filetype) -> None:
        """
        Implements method from Model class. In this implementation, what is intended to be read is
        a .txt (text), .xhtml (HTML), or .md (markdown) file containing help content. If .md is read, that help content is
        converted to xhtml and stored in the HelpModel as a string. If .txt is read, no conversion is done
        and the text as read is stored in the HelpModel as a string.
        :parameter file: A file-like object from which to read the model data.
        :parameter filetype: A string indicating the type of file (i.e., 'txt', 'xhtml', or 'md').
        :return: None
        """
        match filetype:

            case 'txt':
                self._txt_content = file.read()

            case 'xhtml':
                self._xhtml_content = file.read()
                # "Sanitize" the xhtml content, for safety/security
                self._xhtml_content = JustHTML(self._xhtml_content, fragment=True).to_html()

            case 'md':
                self._md_content = file.read()
                html =  markdown(self._md_content)
                # "Sanitize" the xhtml content, for safety/security
                self._xhtml_content = JustHTML(html, fragment=True).to_html()
                # Surround with  <body> </body> tags so it is legal HTML.
                # Because the call to markdown(...) produces a fragment.
                self._xhtml_content = f"<body>{self._xhtml_content}</body>"

        return None


