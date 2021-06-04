import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msg
from tkinter import Spinbox
from datetime import date, datetime, timedelta
from sharkbot.tempBot import SharkBotTemp

from bot_launcher import Launcher

class SharkGui():
    def __init__(self):         # Initializer method
        # Create instance
        self.win = tk.Tk()   
        
        
        # Add a title       
        self.win.title("SHARK BOT")

        # Change the main windows icon
        self.win.iconbitmap('gui/assets/sharkbot.ico')      

        # Launch bot settings
        self.launcher = Launcher()
        self.logger = self.launcher.logger
        self.logger.info("Logger and configuration details successfully set")


        # draw widgets
        self.create_widgets()

    # Button to start Bot execution
    def start_bot(self): 
        self.bot_button.configure(text='Starting  ' + self.number_of_bots_chosen.get() + ' Bidders')
        # check for expiry
        expiry_date = self.launcher.check_expiry()
        if (expiry_date > datetime.now()):
            difference = expiry_date - datetime.now()
            self.logger.info("Executing trial version. You have %s days remaining.", difference.days)
            self.initialize_bots()
        else:
            msg.showerror('SharkBot Message Error Box', 'Your trial period has expired.') 

    def initialize_bots(self):
        """Function to initialize and run bot"""
        # Initialize producer bot
        main_bot = SharkBotTemp(user_details,settings, logger)
        # initalize multple worker bots
        bot_1 = SharkBotTemp(user_details,settings, logger)
        bot_2 = SharkBotTemp(user_details,settings, logger)
        # log in for all bots
        main_bot.start_bot()
        bot_1.start_bot()
        bot_2.start_bot()


        # Spinbox callback 
    def _spin(self):
        value = self.bot_delay_spin.get()
        print(value)
        self.scrol.insert(tk.INSERT, value + '\n')




        # Exit GUI cleanly
    def _quit(self):
        self.win.quit()
        self.win.destroy()
        exit() 
                  
    #####################################################################################       
    def create_widgets(self):    
        tabControl = ttk.Notebook(self.win)          # Create Tab Control
        
        tab1 = ttk.Frame(tabControl)            # Create a tab 
        tabControl.add(tab1, text='Tab 1')      # Add the tab
        tab2 = ttk.Frame(tabControl)            # Add a second tab
        tabControl.add(tab2, text='Tab 2')      # Make second tab visible
        
        tabControl.pack(expand=1, fill="both")  # Pack to make visible
        
        # LabelFrame using tab1 as the parent
        main_window = ttk.LabelFrame(tab1, text='SharkBot Settings')
        main_window.grid(column=0, row=0, padx=8, pady=4)
        
        # Modify adding a Label using mighty as the parent instead of win
        a_label = ttk.Label(main_window, text="Choose Bot Delay:")
        a_label.grid(column=0, row=0, sticky='W')
    
    
        # Adding a Spinbox widget
        self.bot_delay_spin = Spinbox(main_window, values=(2, 4, 6, 8, 10, 12, 15,20, 25, 30, 60, 120, 240), width=5, bd=9, command=self._spin)# using range
        self.bot_delay_spin.grid(column=0, row=1)
                      
        
        # Adding a Button
        self.bot_button = ttk.Button(main_window, text="Start Bot!", command=self.start_bot)   
        self.bot_button.grid(column=2, row=1)                                
        
        ttk.Label(main_window, text="Choose number of bidders:").grid(column=1, row=0)
        self.number_of_bots = tk.StringVar()
        self.number_of_bots_chosen = ttk.Combobox(main_window, width=12, state='readonly', textvariable=self.number_of_bots)
        self.number_of_bots_chosen['values'] = (1, 2, 3, 4, 5, 6)
        self.number_of_bots_chosen.grid(column=1, row=1)
        self.number_of_bots_chosen.current(2)
        
             

        # Using a scrolled Text control    
        scrol_w  = 30
        scrol_h  =  3
        self.scrol = scrolledtext.ScrolledText(main_window, width=scrol_w, height=scrol_h, wrap=tk.WORD)
        self.scrol.grid(column=0, row=3, sticky='WE', columnspan=3)                    
        
        
        # Tab Control 2 ----------------------------------------------------------------------
        # We are creating a container frame to hold all other widgets -- Tab2

            
        # Creating a Menu Bar
        menu_bar = Menu(self.win)
        self.win.config(menu=menu_bar)
        
        # Add menu items
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Display a Message Box
        def _msgBox():
            msg.showinfo('SharkBot Message Info Box', 'SharkBot Bidder: Apply for multiple orders at the best speed possible.')  
            
        # Add another Menu to the Menu Bar and an item
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=_msgBox)   # display messagebox when clicked
        menu_bar.add_cascade(label="Help", menu=help_menu)

        #########################################################################
        # display settings
        self.scrol.insert(tk.INSERT, self.launcher.bot_settings)



        


        

        
   
         
#======================
# Start GUI
#======================
sharkgui = SharkGui()
sharkgui.win.mainloop()
