# standard imports
import tkinter as tk
from tkinter import ttk
from threading import Thread

# local imports
# -- Leave these next two imports EXACTLY how they are, so that tkUserResponseCollector correctly changes values of globals in UserResponseCollector --
import UserQueryReceiver
import tkSimulatorViewManager
import tkUserQueryReceiver
# -- End Leave --
from tkApp import tkApp, AppAboutInfo
from tkUserQueryViewManager import tkUserQueryViewManager
from tkSimulatorViewManager import tkSimulatorViewManager
from SimulatorModel import SimulatorModel


class tkSimulatorApp(tkApp):
    """
    Class is a child of tkApp, extending it's functionality for "simulator" type applications, where there is a
    simulator engine that is "in control", rather than control being the user interacting with the GUI. The GUI
    becomes a thin shell for launching the simulator on a separate thread. The simulator then progresses as it
    wishes, but periodically requests input from the user through tkUserQueryReceiver, and periodically uses
    logging to send output caught by tkSimulatorViewManager.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The top-level tkinter widget, typicaly the return value from tkinter.Tk()
        """
        info = AppAboutInfo(name='Simulator Application', version='0.1', copyright='2025', author='Kevin R. Geurts',
                                  license='MIT License', source='https://github.com/KevinRGeurts/tkAppFramework',
                                  help_file='.\\Help\\SimApp_HelpFile.txt')
        menu_dictionary = {'File':{'Start Simulator':self.onStartSimulator, 'End Simulator':self.onEndSimulator, 'Exit':self.onFileExit},
                           'Help':{'View Help...':self.onViewHelp, 'About...':self.onHelpAbout}}
        super().__init__(parent, title="Simulator Application", menu_dict=menu_dictionary, app_info=info)

        # Thread on which the Simulator will be run
        self._sim_thread = None

    def _createViewManager(self):
        """
        Factory method to create the view manager for the app.
        """
        return tkSimulatorViewManager(self)

    def _createModel(self):
        """
        Factory method to create the model (simulator) for the app.
        :return: The model for the app, simulator
        """
        model = SimulatorModel()
        return model

    def _setup_child_widgets(self):
        """
        Utility function of tkApp class extended here to set up tkUserQueryViewManager. 
        :return: None
        """
        super()._setup_child_widgets()

        # Setup for tkUserQueryViewManager
        self._query_view_manager = tkUserQueryViewManager(self)
        # Attach view manager as observer of model, because tkViewManager.onDestroy() will attempt detach
        self.getModel().attach(self._query_view_manager)
        self._query_view_manager.grid(column=0, row=0, sticky='NWES') # Grid-1 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(0, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx

        # Adjust grid setting for self._view_manager, since we want the UserQueryEntry at the top.
        self._view_manager.grid(column=0, row=1, sticky='NWES') # Grid-1 in Documentation\UI_WireFrame.pptx
        self.columnconfigure(0, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx
        self.rowconfigure(1, weight=1) # Grid-1 in Documentation\UI_WireFrame.pptx

        return None

    @property
    def sim_output_queue(self):
        return self._view_manager.sim_output_queue
        
    def onExit(self):
        """
        Method called when menu item File | Exit is selected.
        """
        self.request_simulator_end()
        self.master.destroy()
        return None
    
    def onStartSimulator(self):
        """
        Method called when menu item File | Start Simulator is selected.
        """
        # TODO: Call some method on the App (now) or mediator (later) that will clean up the UI ahead of the new simulation, since the previous simulation may have been terminated
        # in the middle. This also requires that the QueryWidget get itself cleaned up.

        if self._sim_thread is None:
            # Call run() method of SimulatorModel, on a new thread
            self._sim_thread = Thread(target=self.getModel().run)
            self._sim_thread.start()
            # Start processing of the tkSimulatorViewManager's simulator event queue
            self._view_manager.SimulatorOutputEventHandler()
            # TODO: The way entryconfig() is used is so cryptic, it cries out for a helper function, which
            # should be defined at the tkApp level.
            # enable File | End Simulator, since we now have a currently running simulation
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['End Simulator'][1], state=tk.NORMAL)
            # disable File | Start Simlator menu item, since we don't want more than one simulator currently running.
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Start Simulator'][1], state=tk.DISABLED)
        else:
            # Do nothing.
            pass

        return None

    def onLoadSimulator(self):
        """
        Method called when menu item File | Load Simulator is selected.
        """
        # TODO: Call some method on the App (now) or mediator (later) that will clean up the UI ahead of the new game, since the previous game may have been terminated
        # in the middle. This also requires that the QueryWidget get itself cleaned up.

        if self._sim_thread is None:
            # # Call play(load_game=True) method of CribbageGame, on a new thread
            # self._game_thread = Thread(target=self._game.play, kwargs={'load_game':True})
            # self._game_thread.start()
            # # Start processing of the tkWindowManager's game event queue
            # self._view_manager.CribbageGameOutputEventHandler()
            # # enable File | End Game, since we now have a currently running game
            # self._menu_file.entryconfig('End Game', state='normal')
            # # disable File | Start Game and File | Load Game menu items, since we don't want more than one game currently running.
            # self._menu_file.entryconfig('Start Game', state='disabled') 
            # self._menu_file.entryconfig('Load Game', state='disabled')
            pass 
        else:
            # Do nothing.
            pass

        return None

    def onEndSimulator(self):
        """
        Method called when menu item File | End Simulator is selected.
        """
        if self._sim_thread:
            self._query_view_manager.reset_widgets()
            self.request_simulator_end()
            # Disable File | End Simulator menu item, since no simulator will now be running
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['End Simulator'][1], state=tk.DISABLED)
            # enable File | Start Simulator, since now we have no running simlator
            self._menuConfigDict['File'][0].entryconfig(self._menuConfigDict['File'][1]['Start Simulator'][1], state=tk.NORMAL)
        else:
            pass

        return None

    def request_simulator_end(self):
        """
        Utility method that places a termination request in the response queue of the tkUserResponseCollector.
        """
        # TODO: Consider changing this so that instead a request to end the simulator is sent to the query widget, and it sends the requrired response
        # to the tkUserResponseCollector. This strikes me as the App getting involved in the business of the query widget.
        
        # Don't do anything if self._sim_thread = None, because there is no running simulator to end.
        
        if self._sim_thread:
            end_sim_response = tkUserQueryReceiver.QueryResponse(query_response='<<QueryingThreadTerminationRequest>>', query_ID='')
            UserQueryReceiver.UserQueryReceiver_GetCommandReceiver().put_response_in_queue(end_sim_response)
            self._sim_thread = None
        else:
            pass
            
        return None
        
        