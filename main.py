# Standard
import tkinter as tk

# Local
from test_tkApp import TesttkApp


if __name__ == '__main__':
    
    """
    Create and launch tkinter-based app.
    """
    
    # Create and configure the app
    root = tk.Tk()
    myapp = TesttkApp(root, title='test application')

    # Start the app's event loop running
    myapp.mainloop()

     