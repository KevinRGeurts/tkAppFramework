"""
Defines custom exceptions for the tkAppFramework package.

Exported Classes:
    None

Exported Exceptions:
    tkAppFrameworkError - Base exception class for all custom exceptions specific to tkAppFramework package.
    NoWidgetTagConfigurationAvailableForXHTMLTag - Custom exception to be raised when there is no tkinter Text widget tag
                                                   configuration available for a given XHTML tag.

Exported Functions:
    None

Logging:
    None
 """


class tkAppFrameworkError(Exception):
    """
    Base exception class for all custom exceptions specific to tkAppFramework package.
    """
    pass


class NoWidgetTagConfigurationAvailableForXHTMLTag(tkAppFrameworkError):
    """
    Custom exception to be raised when there is no tkinter Text widget tag configuration available for a given
    XHTML tag.
    Arguments expected in **kwargs: none currently
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # self.X_info = kwargs.get('X_info')


class tkDGElementTextInvalidEntryError(tkAppFrameworkError):
    """
    Custom exception to be raised when a user enters invalid text into a tkDGElementText Entry widget.
    Arguments expected in **kwargs: none currently
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # self.X_info = kwargs.get('X_info')


