# Standard
import tkinter as tk

# Local
from tkApp import tkApp


if __name__ == '__main__':
    
    """
    Create and launch tkinter-based app.
    """
    
    # Create and configure the app
    root = tk.Tk()
    myapp = tkApp(root, title='base application')

    # Start the app's event loop running
    myapp.mainloop()

     