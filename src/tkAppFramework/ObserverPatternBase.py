"""
This module provides Observer and Subject classes that can be a parent of classes that implement an Observer design pattern.

Exported Classes:
    Observer -- Base class for all objects that will be an Observer in an Observer design pattern.
        All Observer child classes should:
            (1) Call register_subject(subject, update_handler) for each Subject object that the Observer child class should observe.
            (2) Define and implement the update_handler functions that are registered with register_subject(...).
                These functions will be called when the Subject object notifies this Observer object by calling notify() on itself.
            (3) Call _detach_from_subjects(), for example, from onDestroy(...), to detach this Observer object from all Subject objects that it is observing.
    Subject -- Base class for all objects that will be a Subject in an Observer design pattern.
        Subjects should attach(...) and detach(...) Observers, and notify() them of changes in state.

Exported Exceptions:
    None
 
Exported Functions:
    None
"""

class UpdateHint:
    """
    Base for optional "hint" provided by a Subject when it calls Update on it's Observers.
    The usage model is that a set of classes that extend Observer and Subject will agree on specific hints,
    and the update describing content encoded in them. This could be done by deriving a set of children of UpdateHint
    and using attributes to encode the update content. In which case the type of the child class would encode the
    type of hint, and attribute values could be specified using **kwargs.
    Arguments expected in **kwargs: none currently
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # self.X_info = kwargs.get('X_info')


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
        :return: None
        """
        for subject in self._subjects:
            subject.detach(self)
        return None

    def update(self, subject, hints = None):
        """
        Acts as a switchboard based on which subject is notifying.
        :parameter subject: Which Subject object is notifying this Observer object, as Subject object
        :parameter hints: An optional list of hints provided by Subject to specify what types of 
                          updates have occurred and details about them, as UpdateHint objects
        :return: None
        """
        assert(isinstance(subject, Subject))
        # Call the updater for the subject argument after looking it up in the _subjects dictionary.
        if hints is not None:
            self._subjects[subject](hints)
        else:
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
        :return: None
        """
        if observer:
            assert(isinstance(observer, Observer))
            self._observers.append(observer)
        return None

    def detach(self, observer=None):
        """
        Detach an observer from the subject.
        :parameter observer: Observer object, instance of Observer class 
        :return: None
        """
        if observer:
            if observer in self._observers:
                self._observers.remove(observer)
        return None

    def notify(self, hints = None):
        """
        Call update(...) on all observers.
        :parameter hints: An optional list of hints to pass to Observer.update() to specify what types of 
                          update have occurred and details about them, as [UpdateHint object]
        :return: None
        """
        for o in self._observers:
            if hints is not None:
                o.update(self, hints)
            else:
                o.update(self)
        return None
