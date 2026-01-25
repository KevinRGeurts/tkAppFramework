"""
This module contains the tkUserQueryToolModal class, which is an abstract base class for modal user query tools that can be
used by a tkUserQueryManager to help the user answer queries posed by the UserQueryReceiver. A defining feature of this
type of tool is that it launches a modal dialog to interact with the user. This module als contains two concrete
implementations of tkUserQueryToolModal: tkPathSaveToolModal and tkPathOpenToolModal.

Concrete implementation child classes of tkUserQueryToolModal must:
    (1) Implement the __init__() method, calling super().__init__() with appropriate tool_name and query_type parameters.
    (2) Implement the run() method to execute the user query tool and return the result as a string.

Exported Classes:
    tkUserQueryToolModal -- Abstract base class modal for user query tools.
    tkPathSaveToolModal -- A modal user query tool that allows the user to select a file path to save as, using the tkinter file dialog.
    tkPathOpenToolModal -- A modal user query tool that allows the user to select a file path to open, using the tkinter file dialog.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""

# Standard library imports
from tkinter import filedialog

# Local application imports
import UserResponseCollector.UserQueryCommand

class tkUserQueryToolModal(object):
    """
    This is an abstract base class for modal user query tools. Modal user query tools can be used by a tkUserQueryManager to help
    the user to answer queries posed by the UserQueryReceiver. A defining feature of this type of tool is that it
    launches a modal dialog to interact with the user.

    Concrete implementation child classes of tkUserQueryToolModal must:
    (1) Implement the __init__() method, calling super().__init__() with appropriate tool_name and query_type parameters.
    (2) Implement the run() method to execute the user query tool and return the result as a string.
    """
    def __init__(self, tool_name = 'A Tool', query_type = None):
        """
        :parameter tool_name: The name of the tool, string
        :parameter query_type: The type of user query command that this tool can answer, UserQueryCommand subclass
        """
        assert(isinstance(tool_name, str) and len(tool_name)>0)
        self._tool_name = tool_name
        
        # Get the list of subclasses of UserQueryCommand
        subs = UserResponseCollector.UserQueryCommand.UserQueryCommand.__subclasses__()
        # Assert that the query_type is UserQueryCommand or a subclass of UserQueryCommand
        assert(query_type == UserResponseCollector.UserQueryCommand.UserQueryCommand or query_type in subs)
        self._query_type = query_type

    @property
    def query_type(self):
        return self._query_type

    @property
    def tool_name(self):
        return self._tool_name

    def run(self):
        """
        Execute the modal user query tool, and return the result, always as a string.
        return: The result of the user query tool, string
        """
        result = ''
        return result


class tkPathSaveToolModal(tkUserQueryToolModal):
    """
    A modal user query tool that allows the user to select a file path to save as.
    """
    def __init__(self):
        """
        Call the parent's __init__() to set the tool name and user query type for the modal user query tool.
        """
        super().__init__(tool_name = 'File Save Path...', query_type = UserResponseCollector.UserQueryCommand.UserQueryCommandPathSave)

    def run(self):
        """
        Run the tool for file path save, in this case, tkinter's filedialog.asksaveasfilename will be used.
        return: The result of the user query tool, string
        """
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(title='File Save Path')
        return response


class tkPathOpenToolModal(tkUserQueryToolModal):
    """
    A modal user query tool that allows the user to select a file path to open.
    """
    def __init__(self):
        """
        Call the parent's __init__() to set the tool name and user query type for the modal user query tool.
        """
        super().__init__(tool_name = 'File Open Path...', query_type = UserResponseCollector.UserQueryCommand.UserQueryCommandPathOpen)

    def run(self):
        """
        Run the tool for file path open, in this case, tkinter's filedialog.askopenfilename will be used.
        return: The result of the user query tool, string
        """
        # Pop up tkFileDialog for open
        response = filedialog.askopenfilename(title='File Open Path')
        return response
