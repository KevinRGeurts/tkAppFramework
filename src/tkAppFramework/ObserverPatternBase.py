"""
This module provides Observer and Subject classes that can be a parent of classes that implement an Observer design pattern.

Exported Classes:
    Observer -- Base class for all objects that will be an Observer in an Observer design pattern.
        All Observer child classes must implement the update(...) method.
    Subject -- Base class for all objects that will be a Subject in an Observer design pattern.
        Subjects should attach(...) and detach(...) Observers, and notify() them of changes in state.

Exported Exceptions:
    None
 
Exported Functions:
    None
"""


class Observer:
    """
    Base class for all objects that will be an Object in an Observer design pattern.

    Child classes must implement the update(...) method.
    """
    def __init__(self):
        # Maintain a dictionary of Key=subject, Value=update handler callable
        self._subjects = {}
        
    def register_subject(self, subject = None, update_handler = None):
        """
        Register a subject and the callable to handle that subject's updates.
        :parameter subject: The Subject object to register, as Subject object
        :parameter update_handler: The callable function to handle updates for subject
        :return: None
        """
        assert(isinstance(subject, Subject))
        assert(callable(update_handler))
        self._subjects[subject]=update_handler
        return None
    
    def _detach_from_subjects(self):
        """
        Detach this observer from all subjects. Called from onDestroy(...).
        :return None:
        """
        for subject in self._subjects:
            subject.detach(self)
        return None

    def update(self, subject):
        """
        Acts as a switchboard based on which subject is notifying.
        :parameter subject: Which Subject object is notifying this Observer object, as Subject object
        :return None:
        """
        assert(isinstance(subject, Subject))
        # Call the updater for the subject argument after looking it up in the _subjects dictionary.
        self._subjects[subject]()
        return None


class Subject:
    """
    Base class for all objects that will a Subject in an Observer design pattern.
    """
    def __init__(self) -> None:
        """
        """
        self._observers = []

    def attach(self, observer=None):
        """
        Attach an observer to the subject.
        :parameter observer: Observer object, instance of Observer class 
        :return None:
        """
        if observer:
            assert(isinstance(observer, Observer))
            self._observers.append(observer)
        return None

    def detach(self, observer=None):
        """
        Detach an observer from the subject.
        :parameter observer: Observer object, instance of Observer class 
        :return None:
        """
        if observer:
            self._observers.remove(observer)
        return None

    def notify(self):
        """
        Call update(...) on all observers.
        :return None:
        """
        for o in self._observers:
            o.update(self)
        return None
