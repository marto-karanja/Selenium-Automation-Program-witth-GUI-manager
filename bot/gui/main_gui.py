#======================
# imports
#======================
import tkinter as tk
from tkinter import ttk

# Create instance
win = tk.Tk()   

# Add a title       
win.title("SharkBot")

# Disable resizing the GUI by passing in False/False
win.resizable(False, False) 

# setting default size
#win.minsize(width=500, height=400)

# Adding a Label
ttk.Label(win, text="Setting up SharkBot").grid(column=0, row=0)

#======================
# Start GUI
#======================
win.mainloop()