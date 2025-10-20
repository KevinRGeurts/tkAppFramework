
# Standard imports
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from collections import namedtuple
from queue import Queue

# Local imports
# -- Leave these next two imports EXACTLY how they are, so that tkUserQueryReceiver correctly changes values of globals in UserQueryReceiver --
import UserQueryReceiver
import tkUserQueryReceiver
# -- End Leave --


class UserQueryWidget(ttk.Labelframe):
    """
    Class represents a tkinter label frame, the wdiget contents of which will allow the user to respond to tkUserQueryReceiver queries.
    It will be necessary for the consumer of this widget to place it within an application's main window, for example.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget
        """
        super().__init__(parent, text='Query')

        # Query queue (FIFO) for communicating QueryInfo objects with the tkUserQueryReceiver object
        self._query_info_queue = Queue(10)
        # A time in seconds to wait when attempting to access a queue with a put or get before timing out
        self._queue_access_timeout = 1
        
        # Set to the QueryInfo object pulled out of the query queue
        self._current_query_info = None

        # Set up tkUserResponseCollector so it has the correct callbacks
        tkUserQueryReceiver.tkUserQueryReceiver_setup(query_event_callback=self.event_generate, query_queue_callback=self.put_query_info_in_queue)

        self.bind('<<TkinterAppQueryEvent>>', self.TkAppQueryEventHandler)

        self.setup_child_widgets()

    def setup_child_widgets(self):
        """
        Utility function to be called by __init__ to set up the child widgets of the query widget.
        :return None:
        """
        # Message widget for showing the query prompt text, that is, the text descibing what query the user is responding too
        self._msg_query = tk.Message(self, relief=tk.RIDGE)
        self._msg_query.grid(column=0, row=0, sticky='NWSE') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        # Control variable for Message widget
        self._msg_query_txt = tk.StringVar()
        # Tell the Message widget to watch this variable.
        self._msg_query["textvariable"] = self._msg_query_txt

        # Query response Entry widget, that is, the entry widget where the user types in their response to the query
        self._ent_response = ttk.Entry(self)
        self._ent_response.grid(column=1, row=0, sticky='NWSE') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(1, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        # Control variable for the Entry widget
        self._ent_response_txt = tk.StringVar()
        # Tell the Entry widget to match this variable.
        self._ent_response["textvariable"] = self._ent_response_txt

        # Enter button
        self._btn_enter = ttk.Button(self, text='Enter', command=self.OnEnterButton)
        self._btn_enter.grid(column=2, row=0) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(2, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        
        # Tools menu button - The menu choices here select "tools" that help the user fill in the Etnry widget text under different circumstances
        # Example, if the user is asked for a file path to save to, they can use the tools menu button to launch a file save dialog.
        self._mbtn_tools = ttk.Menubutton(self, text='Tools')
        self._mbtn_tools.grid(column=3, row=3) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(3, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        # Tools menu button menu
        self._menu_tools = tk.Menu(self._mbtn_tools)
        self._mbtn_tools['menu'] = self._menu_tools
        self._menu_tools.add_command(label='File Save Path...', command=self.OnFileSavePath)
        self._menu_tools.add_command(label='File Open Path...', command=self.OnFileOpenPath)
        
        self.reset_wdigets()

        return None
    
    def OnFileSavePath(self):
        """
        Help respond to a file save path query by using the tkFileDialog for save to get the path.
        """
        # Pop up tkFileDialog for save
        response = filedialog.asksaveasfilename(title='File Save Path')
        # Drop the response into the Entry widget
        self._ent_response_txt.set(response)
        return None
    
    def OnFileOpenPath(self):
        """
        Help respond to a file open path query by using the tkFileDialog for open to get the path.
        """
        # Pop up tkFileDialog for open
        response = filedialog.askopenfilename(title='File Open Path')
        # Drop the response into the Entry widget
        self._ent_response_txt.set(response)
        return None

    def put_query_info_in_queue(self, query_info):
        """
        Called (through a callback) by tkUserQueryReceiver, to put a QueryInfo object in the query widget's query queue
        """
        item = self._query_info_queue.put(query_info, timeout=self._queue_access_timeout)
        return None

    def OnEnterButton(self):
        """
        Called when Enter button is clicked.
        """
        # Get line of text from response Entry widget
        response = self._ent_response_txt.get()
        if len(response)>0:
            # Create QueryResponse object
            query_response=tkUserQueryReceiver.QueryResponse(query_response=response, query_ID=self._current_query_info.query_ID)
            # Place QueryResponse object in tkUserResponseCollector's response queue
            UserQueryReceiver.UserQueryReceiver_GetCommandReceiver().put_response_in_queue(query_response)

            self.reset_wdigets()
        
        return None

    def TkAppQueryEventHandler(self, event):
        """
        Called to handle a <<TkinterAppQueryEvent>> virtual event generated by tkUserQueryReceiver.
        """
        self.handle_query_event()
        return None

    def handle_query_event(self):
        """
        Handle a query event.
        """
        # Retrieve an item from the game event queue to determine what type of information we need from the user
        item = self._query_info_queue.get(timeout=self._queue_access_timeout)
        # Store the QueryInfo that we just retrieved, so that we can access it's ID when we respond
        self._current_query_info = item
        # Populate the message text widget with the preface from the query
        self._msg_query_txt.set(item.prompt_text)
        # Activate the enter button
        self._btn_enter.state(['!disabled'])

        return None

    def reset_wdigets(self):
        """
        Reset all child widgets to a state appropriate for no query yet received, or waiting for the next query to be received.
        """
        self._msg_query_txt.set('--')
        self._ent_response_txt.set('')
        self._btn_enter.state(['disabled'])
        return None


