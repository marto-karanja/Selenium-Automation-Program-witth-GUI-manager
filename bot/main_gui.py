import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msg
from tkinter import Spinbox

class SharkGui():
    def __init__(self):         # Initializer method
        # Create instance
        self.win = tk.Tk()   
        
        
        # Add a title       
        self.win.title("SHARK BOT")

        # Change the main windows icon
        self.win.iconbitmap('gui/assets/sharkbot.ico')      
        self.create_widgets()