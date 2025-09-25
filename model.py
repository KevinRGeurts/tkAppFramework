"""
Defines the abstract base class Model, from which classes representing the data and business logic of an application
should be derived.

Concrete implementation child classes must:
    (1) ...
Concrete implementation child classes likely will:
    (2) ...
Concreate implementation child classes may:
    (3) ...

Exported Classes:
    Model -- Interface (abstract base) class for classes representing the data and business logic
             of an application. Model is a Subject in the Observer design pattern.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# standard imports

# local imports
from ObserverPatternBase import Subject


class Model(Subject):
    """
    Model is the abstract base class from which classes representing the data and business logic of an application
    should be derived.
    """
    def __init__(self) -> None:
        """Initialize the Model."""
        super().__init__()
        # Initialize model data here


