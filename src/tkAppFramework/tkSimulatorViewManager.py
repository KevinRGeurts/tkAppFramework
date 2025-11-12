"""
Defines tkSimulatorViewManager class, which is a concrete implementation of tkViewManager for simulator applications.

tkSimulatorViewManager handles the interactions between output widgets in a tkinter based simulator application.
This class monitors an internal Queue of output events from the simulator, which runs on a separate thread from the
tkinter application. The internal queue will be the designated target of a logging.handler.QueueHandler,
and the simulator will use logging to place output events into the internal queue. The tkSimulatorViewManager
displays these output events to the user through it's SimulatorShowInfoWidget.

Exported Classes:
    tkSimulatorViewManager -- Is-A tkSimulatorViewManager implementation for simulator applications.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    None
"""


# Standard imports
from logging import LogRecord
import tkinter as tk
from tkinter import ttk
from queue import Queue

# Local imports
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject

class tkSimulatorViewManager(tkViewManager):
    """
    tkSimulatorViewManager IS-A tkViewManager, and handles the interactions between output widgets in a tkinter based
    simulator application. This class monitors an internal Queue of output events from the simulator, which runs on a
    separate thread from the tkinter application. The internal queue will be the designated target of a logging.handler.QueueHandler,
    and the simulator will use logging to place output events into the internal queue. The tkSimulatorViewManager
    displays these output events to the user through it's SimulatorShowInfoWidget.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, The tkinter App
        """
        super().__init__(parent)

        # Event queue (FIFO) for communicating with the thread running the simulator, intended for simulator output events
        # Queue size must be big enough that it can handle the amount of logging from the simulator that happens between queries. (Note: 10 was too small.)
        self._sim_event_queue = Queue(100)
        # A time in seconds to wait when attempting to access a queue with a put or get before timing out
        self._queue_access_timeout = 1
        parent.master.bind('<<SimulatorOutputEvent>>', self.SimulatorOutputEventHandler)

    @property
    def sim_output_queue(self):
        return self._sim_event_queue

    def reset_widgets_for_new_simulation(self):
        """
        Utility function called to put child widgets in appropriate state ahead of a new simulation.
        :return: None
        """
        return None

    def SimulatorOutputEventHandler(self, event=None):
        """
        Method which handles output events from simulator which the simulator expects the tkSimulatorApp to visualize and the app expects
        the tkSimulatorViewManager to visualize.
        :parameter event: The tkinter event object associated with this event handler call. Default is None.
        :return None:
        """
        if not self._sim_event_queue.empty():
            # Retrieve a LogRecord from the simulator event queue
            info = self._sim_event_queue.get(timeout=self._queue_access_timeout)
            
            # Make sure we are retrieving what we think we are retrieving, that is, a LogRecord object
            assert(isinstance(info, LogRecord))

            # Put the message from the Log Record in the SimulatorShowInfoWidget
            self._info_widget.insert_end(info.message)

        # Schedule the next execution of this handler
        # First argument to master is delay time (which is in microseconds)
        self.master.master.after(1, self.SimulatorOutputEventHandler)
        return None

    def _CreateWidgets(self):
        """
        Utility function to be called by tkViewManager.__init__ to set up the child widgets of the tkSimulatorViewManager widget.
        This method could be extended by a child class, in the event that the child class wanted to add additional widgets for
        displaying simulator output.
        :return None:
        """
        self._info_widget = SimulatorShowInfoWidget(self)
        self.register_subject(self._info_widget, self.handle_info_widget_update)
        self._info_widget.attach(self)
        self._info_widget.grid(column=1, row=4, columnspan=2, sticky='NWES') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(1, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(4, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        return None

    def handle_model_update(self):
        """
        Handler function called when the SimulatorModel object notifies the tkSimulatorViewManager of a change in state.
        Currently does nothing.
        :return None:
        """
        # Do nothing
        # TODO: Determine if this should do something.
        return None

    def handle_info_widget_update(self):
        """
        Handler function called when the SimulatorShowInfoWidget object notifies the tkSimulatorViewManager of a change in state.
        Currently does nothing.
        :return None:
        """
        # Do nothing
        # TODO: Determine if this should do something.
        return None


class SimulatorShowInfoWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which will display simulator output to the user
    during a simulation.
    :parameter parent: The parent widget of this widget, The tkSimulatorViewManager
    """
    def __init__(self, parent) -> None:
        super().__init__(parent, text='Simulation Output', takefocus=0)
        Subject.__init__(self)
        
       # Create a text widget which will display all the logging.info messages received from the simulator
       
        self._txt_info =  tk.Text(self, width=40, height=10)
        self._txt_info.grid(column=0, row=0, sticky='NWSE') # Grid-2 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-2 in Documentation\UI_WireFrame.pptx
        # Set wrap to NONE, so that there are no line breaks
        self._txt_info['wrap']=tk.NONE

        # Create a vertical Scrollbar and associate it with _txt_info
        self._scrollbar_vert = ttk.Scrollbar(self, command=self._txt_info.yview)
        self._scrollbar_vert.grid(column=1, row=0, rowspan=2, sticky='NWSE')
        self._txt_info['yscrollcommand'] = self._scrollbar_vert.set

        # Create a horizontal Scrollbar and associate it with _txt_info
        self._scrollbar_horz = ttk.Scrollbar(self, command=self._txt_info.xview, orient=tk.HORIZONTAL)
        self._scrollbar_horz.grid(column=0, row=1, columnspan=2, sticky='NWSE')
        self._txt_info['xscrollcommand'] = self._scrollbar_horz.set

        # Set state to DISABLED so the user can't add or change content
        self._txt_info['state']=tk.DISABLED

    def insert_end(self, message=''):
        """
        Utility function to insert a message at the end of the Text widget.
        :parameter message: The message (text) to insert at the end of the Text widget. Default is empty string.
        :return: None
        """
        # Set state to NORMAL so we can insert text
        self._txt_info['state']=tk.NORMAL
        self._txt_info.insert('end', f"{message}\n")
        # Force cursor to last line of text widget, so that the text widget "scrolls to the last line"
        self._txt_info.yview_moveto(1.0)
        # Set state to DISABLED so the user can't add or change content
        self._txt_info['state']=tk.DISABLED
        # Let observers know that state has changed
        self.notify()
        return None
