"""
This module defines the tkUserQueryToolEmbedded class. It represents an abstract base class for  embedded user query tools (widgets) 
for responding to particular types of queries from tkUserQueryReceiver. Instances of this class are created by tkUserQueryViewManager,
which "embeds" them into its own ttk.Frame when needed.

Concrete implementation child classes of tkUserQueryToolEmbedded must:
        (1) Implement the __init__() method, calling super().__init__() with appropriate tool_name and query_type parameters.
        (2) Implement the _CreateWidgets() method to create the child widgets of the tool widget.
        (3) Implement the setup_query() method to populate and set the state of child widgets, appropriately to handle a specific query.
        (4) Implement the disable() method, to set if the tool widget is enabled or disabled, by applying the appropriate state to its child widgets.

Once setup_query() method is called, then it is the responsibility of any event handlers to respond to user interaction,
and set the response property appropriately for the user's response to the query. The response property setter will notify
Observers that a response has been set, and thus that the user has responded to the query.

Exported Classes:
    tkUserQueryToolEmbedded -- Abstract base class for query response tool widgets.
    tkMenuResponseToolWidget -- A query response tool widget that allows the user to select from a menu of options, using a menu button.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard library imports
import tkinter as tk
from tkinter import ttk
from functools import partial

# Local imports
from tkAppFramework.ObserverPatternBase import Subject
import UserResponseCollector.UserQueryCommand


class tkUserQueryToolEmbedded(ttk.Labelframe, Subject):
    """
    This is an abstract base class for embedded user query tools (widgets). It is both a ttk.Labelframe and a Subject.
    These widgets can be used by a tkUserQueryViewManager to help the user to answer queries posed by the
    tkUserQueryReceiver. Instances of this class are created by tkUserQueryViewManager, which "embeds" them into its own ttk.Frame when needed.

    Concrete implementation child classes of tkUserQueryTool must:
        (1) Implement the __init__() method, calling super().__init__() with appropriate tool_name and query_type parameters.
        (2) Implement the _CreateWidgets() method to create the child widgets of the tool widget.
        (3) Implement the setup_query() method to populate and set the state of child widgets, appropriately to handle a specific query.
        (4) Implement the disable() method, to set if the tool widget is enabled or disabled, by applying the appropriate state to its child widgets.

    Once setup_query() method is called, then it is the responsibility of any event handlers to respond to user interaction,
    and set the response property appropriately for the user's response to the query. The response property setter will notify
    Observers that a response has been set, and thus that the user has responded to the query.
    """
    def __init__(self, parent, tool_name = 'A Tool Widget', query_type = None):
        """
        :parameter parent: tkinter widget that is the parent of this widget
        :parameter tool_name: The name of the embedded user query tool (widget), string
        :parameter query_type: The type of user query command that this embedded user query tool (widget) can answer, UserQueryCommand subclass
        """
        assert(isinstance(tool_name, str) and len(tool_name)>0)
        label = f"Query Response - {tool_name}"
        ttk.Labelframe.__init__(self, parent, text=label)
        Subject.__init__(self)

        self._tool_name = tool_name
        
        # Get the list of subclasses of UserQueryCommand
        subs = UserResponseCollector.UserQueryCommand.UserQueryCommand.__subclasses__()
        # Assert that the query_type is UserQueryCommand or a subclass of UserQueryCommand
        assert(query_type == UserResponseCollector.UserQueryCommand.UserQueryCommand or query_type in subs)
        self._query_type = query_type

        self._response = ''

        self._CreateWidgets()

    @property
    def query_type(self):
        return self._query_type

    @property
    def tool_name(self):
        return self._tool_name

    @property
    def response(self):
        """
        Get the query response text from the embedded user query tool (widget).
        :return: Query response text, string
        """
        return self._response

    @response.setter
    def response(self, value):
        """
        Set the query response text from the embedded user query tool (widget), and notify observers.
        :parameter value: The value to which to set the response property, any
        """
        self._response = value
        self.notify()

    def _CreateWidgets(self):
        """
        This abstract method is called by __init__() to create the child widgets of the embedded user query tool (widget).
        It must be implemented by concrete child classes. Will raise NotImplementedError if called.
        :return None:
        """
        raise NotImplementedError
        return None

    def setup_query(self, extra):
        """
        This method should be called to populate and set state of child widgets of the embedded user query tool (widget)
        appropriately to handle a query. It must be extended by concrete child classes.
        Will raise AssertionError if "extra" is not a dictionary.
        :parameter extra: Dictionary of key/value pairs of optional "extra" info passed to tkUserQueryReceiver. Expected
                          to contain the info a  tkUserQueryToolEmbedded needs to set up for a query.
        :return: None
        """
        assert(type(extra)==dict)
        return None

    def disable(self, disabled=True):
        """
        This abstract method is used to set if the embedded user query tool (widget) is enabled or disabled.
        It must be implemented by concrete child classes. Will raise NotImplementedError if called.
        :parameter disabled: True if the embedded user query tool (widget) should be disabled,
                             False if it should be enabled, boolean
        :return None:
        """
        raise NotImplementedError
        return None


class tkMenuUserUserQuerytToolEmbedded(tkUserQueryToolEmbedded):
    """
    Class is a concrete implementation of a tkUserQueryToolEmbedded. Handels UserQueryCommandMenu type queries.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        super().__init__(parent, tool_name='Menu', query_type=UserResponseCollector.UserQueryCommand.UserQueryCommandMenu)

        self._choices = {}

    def _CreateWidgets(self):
        """
        This method is called by super.__init__() to create the child widgets of the embedded user query tool (widget).
        :return None:
        """
        # Menu response menu button for showing/selecting from the menu choices
        self._mbtn_menu_response = ttk.Menubutton(self, text='Choices', takefocus=1)
        self._mbtn_menu_response.grid(column=0, row=0) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-3 in Documentation\UI_WireFrame.pptx
        # Menu response menu button menu
        self._menu_menu_response = tk.Menu(self._mbtn_menu_response)
        self._mbtn_menu_response['menu'] = self._menu_menu_response
        return None

    def setup_query(self, extra):
        """
        This method should be called to populate and set state of child widgets of the embedded user query tool (widget)
        appropriately to handle a query.
        :parameter extra: Dictionary of key/value pairs of optional "extra" info passed to tkUserQueryReceiver. Expected
                          to contain the info a  tkUserQueryToolEmbedded needs to set up for a query.
        :return: None
        """
        super().setup_query(extra)

        # TODO: What if extra does not contain 'query_dic' key? Handle.
        query_dic = extra['query_dic']
        assert(type(query_dic)==dict)
        self._choices = query_dic

        # Remove any current commands from the menu
        self._menu_menu_response.delete(0, self._menu_menu_response.index(tk.END))
        # Populate the menu with commands for the menu choices
        for key in self._choices:
            self._menu_menu_response.add_command(label = str(self._choices[key]), command = partial(self.onSelectChoice, key))

        return None

    def onSelectChoice(self, key):
        """
        Handle selection of a menu choice from the menu.
        :parameter key: Key of the choice selected from the menu, string
        :return: None
        """
        assert(isinstance(key, str) and key in self._choices)
        self.response = key
        return None

    def disable(self, disabled=True):
        """
        Used to set if the embedded user query tool (widget) is enabled or disabled.
        :parameter disabled: True if the embedded user query tool (widget) should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._mbtn_menu_response.state(['disabled'])
        else:
            self._mbtn_menu_response.state(['!disabled'])
        return None
