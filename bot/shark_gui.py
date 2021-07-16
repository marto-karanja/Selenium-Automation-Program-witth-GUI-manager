from sys import maxsize
import wx
import threading
import time
from queue import Queue
from datetime import datetime

from sharkbot.tempBot import SharkBotTemp

from bot_launcher import Launcher

class SharkFrame(wx.Frame):
    """Initializes main Shark Bot Frame"""
    def __init__(self):
        # Launch bot settings
        self.launcher = Launcher()
        self.consumer_bots = []
        self.active_threads = []
        self.logger = self.launcher.logger
        self.logger.info("Logger and configuration details successfully set")
        wx.Frame.__init__(self, None, title="SharkBot Control Panel")
        # set icon
        self.SetIcon(wx.Icon("gui/assets/sharkbot.ico"))

        panel = wx.Panel(self)
        self.startBtn = wx.Button(panel, -1, "Start Bidding Bots")
        stopBtn  = wx.Button(panel, -1, "Stop all Bidding Bots")
        self.tc = wx.StaticText(panel, -1, "Active Bidding Bots: 00")
        self.logTxtField = wx.TextCtrl(panel, -1, "",
                               style=wx.TE_RICH|wx.TE_MULTILINE)

        delay_combo_text = wx.StaticText(panel, -1, "Choose Delay in Seconds")
        bidder_combo_text = wx.StaticText(panel, -1, "Choose No. Of Bidders")
        bid_status_combo_text = wx.StaticText(panel, -1, "Choose Bid Status")

        delay = ['1','2','3','4','5','10','15','20']
        self.bot_delay_combo = wx.ComboBox(panel, -1, "Choose Delay in Seconds", (15, 30), (150,25), delay, wx.CB_DROPDOWN|wx.CB_READONLY)
        self.bot_delay_combo.SetValue(delay[1])
        self.bot_choices = {'1 Bidder':'1', '2 Bidders': '2','3 Bidders': '3', '4 Bidders': '4', '5 Bidders':'5', '6 Bidders': '6'}
        bot_combo_values = list(self.bot_choices.keys())
        self.bot_bidder_combo = wx.ComboBox(panel, -1, "Choose No. Of Bidders", (15, 30), (150,25), bot_combo_values, wx.CB_DROPDOWN|wx.CB_READONLY)
        bid_status_choices = ['True', 'False']
        self.bid_status_combo = wx.ComboBox(panel, -1, "Choose Bid status", (15, 30), (150,25), bid_status_choices, wx.CB_DROPDOWN|wx.CB_READONLY)
        self.bid_status_combo.SetValue(self.launcher.bot_settings['bid_status'])
        self.bot_bidder_combo.SetValue(bot_combo_values[1])

        # Add a progress bar
        #self.progress_bar = wx.Gauge( panel, -1, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        #self.progress_bar.SetValue( 0 )
        
        ### Add a filter settings button

        # Use GridBagSizer for layout
        control_panel_sizer = wx.GridBagSizer(hgap=10, vgap=10)
        control_panel_sizer.Add(delay_combo_text, pos = (0,0), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(bidder_combo_text, pos = (0,1), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(bid_status_combo_text, pos = (0,2), flag= wx.EXPAND | wx.CENTER, border=10)
        # Combo Box options
        control_panel_sizer.Add(self.bot_delay_combo, pos = (1,0), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.bot_bidder_combo, pos = (1,1), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.bid_status_combo, pos = (1,2), flag= wx.EXPAND | wx.CENTER, border=10)
        # Button options row
        control_panel_sizer.Add(self.startBtn, pos = (2,0), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(stopBtn, pos = (2,1), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.tc, pos = (2,2), border=10)
        # Add Progress bar
        #control_panel_sizer.Add(self.progress_bar, pos=(3,0),  border=10, span=(1,3), flag=wx.EXPAND)


        #TO DO:  resizing logic
        control_panel_sizer.AddGrowableCol(0)
        control_panel_sizer.AddGrowableCol(1)
        control_panel_sizer.AddGrowableCol(2)



        control_holder = wx.BoxSizer(wx.VERTICAL)
        control_holder.Add(control_panel_sizer, 1, wx.EXPAND|wx.ALL, 10)        

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(control_holder)
        main_sizer.Add(self.logTxtField, 1, wx.EXPAND|wx.ALL, 5)

        panel.SetSizer(main_sizer)



        """
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(startBtn, 0, wx.RIGHT, 15)
        button_sizer.Add(stopBtn, 0, wx.RIGHT, 15)
        button_sizer.Add(self.tc, 0, wx.ALIGN_CENTER_VERTICAL)
        # Add static text row
        static_text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        static_text_sizer.Add(delay_combo_text,0, wx.RIGHT,15)
        static_text_sizer.Add(bidder_combo_text,0, wx.CENTER,15)
        static_text_sizer.Add(bid_status_combo_text,0, wx.RIGHT,15)
        # Add second row
        options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        options_sizer.Add(self.bot_delay_combo,0, wx.RIGHT,15)
        options_sizer.Add(self.bot_bidder_combo,0, wx.RIGHT,15)
        options_sizer.Add(self.bid_status_combo,0, wx.RIGHT,15)
        # Add third row for progress bar
        progress_sizer = wx.BoxSizer(wx.VERTICAL)
        progress_sizer.Add(self.progress_bar,0, wx.ALL|wx.EXPAND, 5)
        
        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(static_text_sizer,0, wx.ALL, 5)       
        main.Add(options_sizer, 0, wx.ALL, 5)
        main.Add(button_sizer, 0, wx.ALL, 5)
        main.Add(progress_sizer, 0, wx.EXPAND|wx.ALL, 5)
        main.Add(self.logTxtField, 1, wx.EXPAND|wx.ALL, 5)
        panel.SetSizer(main)"""

        
        self.Bind(wx.EVT_BUTTON, self.OnStartButton, self.startBtn)
        self.Bind(wx.EVT_BUTTON, self.OnStopButton, stopBtn)
        self.Bind(wx.EVT_CLOSE,  self.OnCloseWindow)

        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.SetSize(565, 495)

        



    def OnStartButton(self, evt):
        expiry_date = self.launcher.check_expiry()
        if (expiry_date > datetime.now()):
            difference = expiry_date - datetime.now()
            self.logger.info("Executing trial version. You have %s days remaining.", difference.days)
            # TO DO
            # Log Active Days on dashboard
            # Deactivate button to prevent clicking
            self.log_message_to_txt_field("Setting up Bidders......")
            self.logger.info("Setting up Bidders......")
            self.initialize_bots()
        else:
            wx.MessageBox('Your trial period has expired.', 'SharkBot Message Error Box',
                          wx.OK | wx.ICON_ERROR)
            return
    def initialize_bots(self):
        """Function to initialize and run bot"""
        # Initialize producer bot
        # start progress bar

        # initalize multple worker bots &
        # log in for all bots
        # Use a for loop to create a list of instances
        bots = []
        self.launcher.bot_settings['bid_status'] = self.bid_status_combo.GetValue()
        choosen_bots = self.bot_bidder_combo.GetValue()
        self.logger.info("ComboBox Value %s",choosen_bots)
        no_of_bots = self.bot_choices[choosen_bots]
        self.update_status_text("1 Main Bot and {} Bidding Bots Running".format(no_of_bots))
        i = 1
        while i <= int(no_of_bots):
            bot_name = "bot_" + str(i)
            bots.append(bot_name)
            i = i + 1
        # disable button
        self.startBtn.Disable()
        # start main producer bot
        ## Start progress bar self.progress_bar.start()

        # create objects for all strings in consumer bots list
        ## To Do: Launch in a thread
        # list to hold consumer objetcs
        self.consumer_bots = []
        for bot in bots:
            bot = SharkBotTemp(self.launcher.user_details,self.launcher.bot_settings, self.logger)
            bot.start_bot()
            self.consumer_bots.append(bot)
            self.log_message_to_txt_field("[Listener Bot]: Starting a listener bot")
        
        self.main_bot = SharkBotTemp(self.launcher.user_details,self.launcher.bot_settings, self.logger)
        self.main_bot.start_main_bot()
        self.log_message_to_txt_field("[Main Bot]: Starting the main bot")
        # Launch threads
        # Launch main thread and post to queue
        self.launch_threads()

    def launch_threads(self):
        # Launch main thread
        # create queue instance
        self.order_queue = Queue(maxsize = 100)
        self.quit_event = threading.Event()
        main_thread = threading.Thread(target=self.main_bot.fetch_queued_orders, args=(self.order_queue, self.quit_event, self), daemon=True)
        # add thread to thread of active threads
        self.active_threads.append(main_thread)
        main_thread.start()
        # Launch children bots
        
        for bot in self.consumer_bots:
            child_bidder = threading.Thread(target= bot.process_queued_orders, args=(self.order_queue, self.quit_event, self), daemon=True)
            self.active_threads.append(child_bidder)
            child_bidder.start()



    def update_status_text(self, message):
        self.tc.SetLabel(message)


    def log_message_to_txt_field(self, msg):
        self.logTxtField.AppendText(msg)
        self.logTxtField.AppendText("\n")


    

    
    def OnStopButton(self, evt):
        if len(self.active_threads) > 0:
            self.logger.info("Stopping all threads...")
            self.quit_event.set()
        self.log_message_to_txt_field("Stopping all Bidding Bots....")
        # Shut Down Chrome driver instances
        time.sleep(30)
        try:
            if self.main_bot.instatiated == True:
                self.main_bot.stop_bot()
        except AttributeError:
            # instance class is not available
            pass
        # close bidder bots
        for bot in self.consumer_bots:
            bot.stop_bot()
        self.startBtn.Enable()
        self.log_message_to_txt_field("All Bidding Bots have stopped")
        self.update_status_text("0 Bots running")
        ## TO DO
        # check if thread is active before joining
        """
        for index, thread in enumerate(self.active_threads):
            self.logger.info("Main    : before joining thread %d.", index)
            # if thread.is_alive():
            thread.join()
            self.logger.info("Main    : thread %d done", index)"""
        
    def OnCloseWindow(self, evt):
        # close active threads????
        """
        """
        if len(self.active_threads) > 0:
            self.logger.info("Stopping all threads...")
            self.quit_event.set()


        # Shut Down Chrome driver instances
        try:
            if self.main_bot.instatiated == True:
                self.main_bot.stop_bot()
        except AttributeError:
            # instance class is not available
            pass
        # close bidder bots
        for bot in self.consumer_bots:
            bot.stop_bot()
        self.Destroy()

app = wx.App()
import locale
locale.setlocale(locale.LC_ALL, 'en_US')
frm = SharkFrame()
frm.Show()
app.MainLoop()