import tkinter as tk
import concurrent.futures
import queue
import threading
# other tkinter imports
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
        self.win.geometry('600x400')
        self.win.call('wm', 'attributes', '.', '-topmost', True)   
        
        
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
        # start progress bar

        # initalize multple worker bots &
        # log in for all bots
        # Use a for loop to create a list of instances
        bots = []
        choosen_bots = int(self.number_of_bots_chosen.get())
        i = 1
        while i <= choosen_bots:
            bot_name = "bot_" + str(i)
            bots.append(bot_name)
            i = i + 1
        self.scrol.insert(tk.INSERT, bots)
        # start main producer bot
        self.progress_bar.start()
        self.main_bot = SharkBotTemp(self.launcher.user_details,self.launcher.bot_settings, self.logger)
        self.main_bot.start_bot()
        # create objects for all strings in consumer bots list
        ## To Do: Launch in a thread
        # list to hold consumer objetcs
        consumer_bots = []
        for bot in bots:
            bot = SharkBotTemp(self.launcher.user_details,self.launcher.bot_settings, self.logger)
            bot.start_bot()
            consumer_bots.append(bot)

        # stop progress bar
        self.progress_bar.stop()

        

        # pass list object to class variable for use in other functions
        self.consumer_bots = consumer_bots
        # create event and queue
        self.pipeline = queue.Queue(maxsize=10)
        self.event = threading.Event()
        self.logger.info("Queue and event object created")

        ## create producer and consumer threads
        max_workers = 5 if 5 > choosen_bots else choosen_bots
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        # creating producer thread
        # store existing orders in the main_order list
        ## store existing orders during bot start up
        fetched_orders = self.main_bot.fetch_orders()
        self.scrol.insert(tk.INSERT, "Initial orders found on Ac")
        self.main_bot.order_list.update(fetched_orders)
        self.scrol.insert(tk.INSERT, self.main_bot.order_list)
        # launch producer thread
        executor.submit(self.main_bot.fetch_queued_orders, self.pipeline, self.event)
        self.logger.info("Main consumer bidding bot created and assigned to thread")

        # creating consumer thread using a for loop
        for bot in self.consumer_bots:
            executor.submit(bot.process_queued_orders, self.pipeline, self.event)

        self.logger.info("Producer consumer bots created")
        self.event.set()
        self.logger.info("Event has been set")

        
        """

        # initialize threads
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        executor.submit(bot_1.process_queued_orders, pipeline, event)
        executor.submit(bot_2.process_queued_orders, pipeline, event)"""

    def stop_bot(self):
        """Stops running threads cleanly"""
        pass


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
        tabControl.add(tab2, text='Bot Settings')      # Make second tab visible
        
        tabControl.pack(expand=1, fill="both")  # Pack to make visible
        
        # LabelFrame using tab1 as the parent
        main_window = ttk.LabelFrame(tab1, text='SharkBot Settings')
        main_window.grid(column=0, row=0, sticky = "nsew", padx=8, pady=4)
        main_window.grid_rowconfigure(0, weight = 1)
        main_window.grid_columnconfigure(0, weight = 1)
        
        # Modify adding a Label using mighty as the parent instead of win
        a_label = ttk.Label(main_window, text="Choose Bot Delay:")
        a_label.grid(column=0, row=0, sticky='W')
    
    
        # Adding a delay combobox
        self.delay_time = tk.StringVar()
        self.delay_combobox =ttk.Combobox(main_window, width=12, state='readonly', textvariable=self.delay_time)
        self.delay_combobox['values'] = ("1 Secs", "2 Secs", "3 Secs", "5 Secs", "10 Secs", "15 Secs", "30 Secs", "45 Secs","60 Secs")
        self.delay_combobox.grid(column=0, row=1)
        self.delay_combobox.current(2)
                      
        
        # Adding a Button
        self.bot_button = ttk.Button(main_window, text="Start Bot!", command=self.start_bot)   
        self.bot_button.grid(column=2, row=1)                                
        
        ttk.Label(main_window, text="Choose number of bidders:").grid(column=1, row=0)
        self.number_of_bots = tk.StringVar()
        self.number_of_bots_chosen = ttk.Combobox(main_window, width=12, state='readonly', textvariable=self.number_of_bots)
        self.number_of_bots_chosen['values'] = (1, 2, 3, 4, 5, 6)
        self.number_of_bots_chosen.grid(column=1, row=1)
        self.number_of_bots_chosen.current(1)
        
        # Add a Progressbar to Tab 2
        self.progress_bar = ttk.Progressbar(main_window, orient='horizontal', length=286, mode='determinate')
        self.progress_bar.grid(column=0, row=3, pady=2, sticky='WE', columnspan=2)
        
        # Adding a stop Button
        self.stop_bot_button = ttk.Button(main_window, text="Stop Bot!", command=self.stop_bot)   
        self.stop_bot_button.grid(column=2, row=3)    
             

        # Using a scrolled Text control    
        scrol_w  = 30
        scrol_h  =  3
        self.scrol = scrolledtext.ScrolledText(main_window, width=scrol_w, height=scrol_h, wrap=tk.WORD)
        self.scrol.grid(column=0, row=4, sticky='WE', columnspan=3)                    
        
        
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
        #self.scrol.insert(tk.INSERT, self.launcher.bot_settings)



        


        

        
   
         
#======================
# Start GUI
#======================
sharkgui = SharkGui()
sharkgui.win.mainloop()
