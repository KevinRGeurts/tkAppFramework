# Standard imports
from logging import LogRecord
import tkinter as tk
from tkinter import ttk
from queue import Queue

# Local imports
from tkViewManager import tkViewManager
from ObserverPatternBase import Subject

class tkSimulatorViewManager(tkViewManager):
    """
    Class follows mediator design pattern. It handles the interactions between widgets in a tkinter based application.
    Ultimately the intent is to use this as a base class, and only implment in it reusable functionality for any tkinter based application
    where non-UI objects are "in control" rather than the tkinter event loop. Think of a "simulation" code that is started and does it's own thing,
    excpet for maybe occassionaly requesting input from a user. The simulation periodically produces output that should be displayed in the tkinter-based
    application. Objects of this class will monitor an internal Queue of output events from the simulation, which runs on a separate thread from the
    tkinter application. The internal queue will be the designated target of a logging.handler.QueueHandler, and the simulator will use logging to place
    output events into the internal queue.
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

    def reset_widgets_for_new_simulation(self):
        """
        Utility function called to put child widgets in appropriate state ahead of a new simulation.
        """
        return None

    def SimulatorOutputEventHandler(self, event=None):
        """
        Method which handles output events from simulator which the simulator expects the tkSimulatorApp to visualize and the app expects
        the tkSimulatorWindowManager to visualize.
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
    """
    def __init__(self, parent) -> None:
        super().__init__(parent, text='Simulation Output')
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

