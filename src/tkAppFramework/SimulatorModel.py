"""
This module provides the SimlatorModel class, which represents the "business logic" of an application for interacting with
a simulator.

Exported Classes:
    SimulatorModel -- This class represents (wraps) the simulator, and is a Model in the MVC pattern.

Exported Exceptions:
    None    
 
Exported Functions:
    None.
"""

# standard imports

# local imports
from tkAppFramework.model import Model


class SimulatorModel(Model):
    """
    This class represents the "business logic" for a tkSimulatorApp interacting with a simulator, and is a Model in the MVC pattern.
    """
    def __init__(self, sim_adapt=None) -> None:
        """
        :parameter sim_adapt: The SimulatorAdapter subclass object that interfaces with the simulator, SimulatorAdapter object
        """
        super().__init__()
        self.sim_adapter = sim_adapt

    @property
    def sim_adapter(self):
        return self._sim_adapter

    @sim_adapter.setter
    def sim_adapter(self, value):
        self._sim_adapter = value
        self.notify()

    def run(self):
        """
        Method called to run the simulator, using the simulator adapter.
        :return: None
        """
        self._sim_adapter.run()
        return None


