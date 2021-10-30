from random import sample
from sys import maxsize
import wx
import threading
import time
from queue import Queue
from datetime import datetime

from sharkbot.tempBot import SharkBotTemp

from bot_launcher import Launcher


class FilterFrame(wx.Frame):
    def __init__(self, parent, main_bot):
        """Window to set filters for main bidding bot"""
        # save main bot as aclass attribute
        self.main_bot = main_bot

        wx.Frame.__init__(self, parent, title='Set bidding Filters', style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP, size = (550, 475))
        panel = wx.Panel(self)
        # create box sizert to hold all sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # create first static box sizer
        top = wx.StaticBox(panel, -1, "Type of service")
        top_settings_sizer = wx.StaticBoxSizer(top, wx.HORIZONTAL)

        #list to hold all checkboxes
        self.filter_checkboxes = []



        sample_writing = wx.CheckBox(panel, -1, label = "Sample Writing", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="sample_writing") 
        editing_or_rewriting = wx.CheckBox(panel, -1, label = "Editing or Rewriting", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="editing_or_rewriting")
        writing_help = wx.CheckBox(panel, -1, label = "Writing help", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="writing_help")

        # Add to list holding all checkboxes
        self.filter_checkboxes.extend([sample_writing, editing_or_rewriting, writing_help])
        # Add to static box sizer
        top_settings_sizer.Add(sample_writing, 0, wx.ALL|wx.CENTER, 5) 
        top_settings_sizer.Add(editing_or_rewriting, 0, wx.ALL|wx.CENTER, 5) 
        top_settings_sizer.Add(writing_help, 0, wx.ALL|wx.CENTER, 5) 

        # create discplines section
        disciplines_choices = {'art':'Art', 'business_and_management':'Business and Management','computer_science':'Computer Science', 'economics':'Economics', 'engineering':'Engineering', 'english_and_literature':'English and Literature','health_care_and_life_sciences':'Health Care and Life Sciences','history':'History','humanities': 'Humanities', 'law': 'Law', 'marketing': 'Marketing', 'mathematics_and_statistics':'Mathematics and Statistics', 'natural_science' : 'Natural science', 'philosophy': 'Philosophy', 'political_science': 'Political science', 'psychology_and_education' : 'Psychology and Education', 'religion_theology':'Religion / Theology', 'social_science': 'Social Sciences'}
        # create list of combo boxes
        disciplines_checkboxes = []
        for key, value in disciplines_choices.items():
            discipline_checkbox  = wx.CheckBox(panel, -1, label = value, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=key)
            disciplines_checkboxes.append(discipline_checkbox)

        # add to Grid Bag Sizer
        discipline_panel_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        col = 0
        row = 0
        for checkbox in disciplines_checkboxes:
            discipline_panel_sizer.Add(checkbox, pos = (row, col), flag= wx.EXPAND | wx.CENTER, border=5)
            if col == 2:
                col = 0
                row = row + 1
            else:
                col = col + 1

        # Add to list holding all checkboxes
        self.filter_checkboxes.extend(disciplines_checkboxes)
        
        disciplines = wx.StaticBox(panel, -1, "Disciplines for Writing Orders")
        disciplines_settings_sizer = wx.StaticBoxSizer(disciplines, wx.HORIZONTAL)
        disciplines_settings_sizer.Add(discipline_panel_sizer)

        # other discpline horizontal box sizer
        other_discipline_checkbox = wx.CheckBox(panel, -1, label = "Other discplines", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="other_disciplines")
        # Add to list holding all checkboxes
        self.filter_checkboxes.append(other_discipline_checkbox)
        other_discipline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        other_discipline_sizer.Add(other_discipline_checkbox)

        # Deadline Section
        deadline_choices = {
            '0_8_hours': '0 - 8 Hours',
            '8_24_hours':  '8-24 hours',
            '1_2_days':  '1-2 days',
            '2_3_days':  '2-3 days',
            '3_5_days': '3-5 days',
            '5_7_days':  '5-7 days',
            '7_10_days': ' 7-10 days',
            '10_days':  '10+ days' ,
            'exceeded_deadline': 'Deadline is exceeded (late)'
        }
        deadline_checkboxes = []
        for key, value in deadline_choices.items():
            deadline_checkbox = wx.CheckBox(panel, -1, label = value, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=key)
            deadline_checkboxes.append(deadline_checkbox)

        # add to grid bag sizer
        # add to Grid Bag Sizer
        deadline_panel_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        col = 0
        row = 0
        for checkbox in deadline_checkboxes:
            deadline_panel_sizer.Add(checkbox, pos = (row, col), flag= wx.EXPAND | wx.CENTER, border=5)
            if col == 4:
                col = 0
                row = row + 1
            else:
                col = col + 1

        # Add to list holding all checkboxes
        self.filter_checkboxes.extend(deadline_checkboxes)

        deadlines = wx.StaticBox(panel, -1, "Deadlines")
        deadlines_settings_sizer = wx.StaticBoxSizer(deadlines, wx.HORIZONTAL)
        deadlines_settings_sizer.Add(deadline_panel_sizer)
        
        # pages section
        pages_choices = {
            '1_5_pages': '1-5 pages',
            '6_10_pages' : '6-10 pages',
            '11_15_pages':'11-15 pages',
            '15_pages' : '15+ pages'

        }
        pages_checkboxes = []
        for key, value in pages_choices.items():
            page_checkbox = wx.CheckBox(panel, -1, label = value, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=key)
            pages_checkboxes.append(page_checkbox)

        # add to grid bag sizer
        # add to Grid Bag Sizer
        page_panel_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        col = 0
        row = 0
        for checkbox in pages_checkboxes:
            page_panel_sizer.Add(checkbox, pos = (row, col), flag= wx.EXPAND | wx.CENTER, border=5)
            if col == 4:
                col = 0
                row = row + 1
            else:
                col = col + 1

        # Add to list holding all checkboxes
        self.filter_checkboxes.extend(pages_checkboxes)

        
        pages = wx.StaticBox(panel, -1, "Pages")
        pages_settings_sizer = wx.StaticBoxSizer(pages, wx.HORIZONTAL)
        pages_settings_sizer.Add(page_panel_sizer)


        # final options section
              
        order_choices = {
            'hide_viewed_orders': 'Hide viewed orders',
            'customers_online' : 'Customers online',
            'hide_orders_placed':'Hide orders placed more than 2 days ago',
            'show_outdated_orders' : 'Show outdated orders'

        }
        order_checkboxes = []
        for key, value in order_choices.items():
            order_checkbox = wx.CheckBox(panel, -1, label = value, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=key)
            order_checkboxes.append(order_checkbox)

        # add to grid bag sizer
        # add to Grid Bag Sizer
        order_panel_sizer = wx.GridBagSizer(hgap=5, vgap=5)
        col = 0
        row = 0
        for checkbox in order_checkboxes:
            order_panel_sizer.Add(checkbox, pos = (row, col), flag= wx.EXPAND | wx.CENTER, border=5)
            if col == 1:
                col = 0
                row = row + 1
            else:
                col = col + 1

        # Add to list holding all checkboxes
        self.filter_checkboxes.extend(order_checkboxes)
        

        # Filter button section
        apply_button = wx.Button(panel, -1, "Apply Filters")
        # add filter button to box sizer
        apply_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        apply_box_sizer.Add(apply_button, -1, wx.RIGHT, 5)
           




        # add to panel
        main_sizer.Add(top_settings_sizer)
        main_sizer.Add(disciplines_settings_sizer, wx.ID_ANY, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(other_discipline_sizer,wx.ID_ANY, wx.EXPAND| wx.ALL, 5)
        main_sizer.Add(deadlines_settings_sizer, wx.ID_ANY, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(pages_settings_sizer, wx.ID_ANY, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(order_panel_sizer, wx.ID_ANY, wx.EXPAND| wx.ALL,10)
        main_sizer.Add(apply_box_sizer, wx.ID_ANY, wx.EXPAND| wx.ALL,10)
        
        panel.SetSizer(main_sizer)

        # Bind event handler
        self.Bind(wx.EVT_BUTTON, self.OnApplyFilters, apply_button)
        
    def OnApplyFilters(self, event):
        # launch filter form
        active_filters = []
        for checkbox in self.filter_checkboxes:
            if checkbox.IsChecked():
                active_filters.append(checkbox.GetName())
            #print (checkbox.GetLabel())
            print (checkbox.GetName())
            #print(checkbox.IsChecked())
        if len(active_filters) > 0:
            if(self.main_bot.set_filters(active_filters)):
                wx.MessageBox('Successfully set filters.', 'SharkBot Filter Info Box', wx.OK | wx.ICON_INFORMATION)
                # close the window
                self.Destroy()
            else:
                wx.MessageBox('Unable to set filters.', 'SharkBot Filter Error Box',
                          wx.OK | wx.ICON_ERROR)


            
        
    
    def OnCloseWindow(self, event):
        self.Destroy()


        

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
        self.accountBtn = wx.Button(panel, -1, "Enter Account Log Ins")
        self.launchBtn = wx.Button(panel, -1, "Launch Bidding Browsers")
        self.startBtn = wx.Button(panel, -1, "Start Bidding Process")
        self.stopBtn  = wx.Button(panel, -1, "Stop all Bidding Bots")
        self.filterBtn = wx.Button(panel, -1, "Change Filters")
        self.tc = wx.StaticText(panel, -1, "Active Bidding Bots: 00")
        self.logTxtField = wx.TextCtrl(panel, -1, "",
                               style=wx.TE_RICH|wx.TE_MULTILINE)

        # Disable buttons
        self.startBtn.Disable()
        self.stopBtn.Disable()
        self.filterBtn.Disable()

        account_button_text = wx.StaticText(panel, -1, "Set Account Log Ins")
        bidder_combo_text = wx.StaticText(panel, -1, "Choose No. Of Bidders")
        bid_status_combo_text = wx.StaticText(panel, -1, "Choose Bid Status")

        """delay = ['1','2','3','4','5','10','15','20']
        self.bot_delay_combo = wx.ComboBox(panel, -1, "Choose Delay in Seconds", (15, 30), (150,25), delay, wx.CB_DROPDOWN|wx.CB_READONLY)
        self.bot_delay_combo.SetValue(delay[1])"""
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
        control_panel_sizer.Add(account_button_text, pos = (0,0), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(bidder_combo_text, pos = (0,1), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(bid_status_combo_text, pos = (0,2), flag= wx.EXPAND | wx.CENTER, border=10)
        # Combo Box options
        control_panel_sizer.Add(self.accountBtn, pos = (1,0), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.bot_bidder_combo, pos = (1,1), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.bid_status_combo, pos = (1,2), flag= wx.EXPAND | wx.CENTER, border=10)
        # Launch button row
        control_panel_sizer.Add(self.launchBtn, pos=(2,0),  border=10, span=(1,3), flag=wx.EXPAND)
        # Button options row
        control_panel_sizer.Add(self.filterBtn, pos = (3,0), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.startBtn, pos = (3,1), flag= wx.EXPAND | wx.CENTER, border=10)
        control_panel_sizer.Add(self.stopBtn, pos = (3,2), flag= wx.EXPAND | wx.CENTER, border=10)
        # Add Status text to colspan row
        control_panel_sizer.Add(self.tc, pos=(4,0),  border=10, span=(1,3), flag=wx.CENTER)

        # Add Progress bar
        #control_panel_sizer.Add(self.progress_bar, pos=(3,0),  border=10, span=(1,3), flag=wx.EXPAND)


        #TO DO:  resizing logic
        control_panel_sizer.AddGrowableCol(0)
        control_panel_sizer.AddGrowableCol(1)
        control_panel_sizer.AddGrowableCol(2)



        control_holder = wx.BoxSizer(wx.VERTICAL)
        control_holder.Add(control_panel_sizer, 1,wx.EXPAND|wx.ALL| wx.CENTER, 20) 
        top = wx.StaticBox(panel, -1, "Control Panel")
        top_settings_sizer = wx.StaticBoxSizer(top, wx.HORIZONTAL)   
        top_settings_sizer.Add(control_holder)    

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_settings_sizer)
        main_sizer.Add(self.logTxtField, 1, wx.EXPAND|wx.ALL, 5)

        panel.SetSizer(main_sizer)

        # create menu
        self.create_menu()



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
        self.Bind(wx.EVT_BUTTON, self.launch_browser, self.launchBtn)
        self.Bind(wx.EVT_BUTTON, self.OnStopButton, self.stopBtn)
        self.Bind(wx.EVT_BUTTON, self.OnFilter, self.filterBtn)
        self.Bind(wx.EVT_BUTTON, self.enter_login, self.accountBtn)
        self.Bind(wx.EVT_CLOSE,  self.OnCloseWindow)

        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.SetSize(565, 495)


    
    def create_menu(self):
        # creating menu bar
        menuBar = wx.MenuBar()
        
        sub_menu = wx.Menu()
        sub_menu.Append(wx.NewIdRef(count=1), "Shark Account Logins")
        sub_on_top_menu = wx.Menu()
        sub_on_top_menu.AppendRadioItem(wx.NewIdRef(count=1), "Yes")
        sub_on_top_menu.AppendRadioItem(wx.NewIdRef(count=1), "No")
    
        sub_menu.AppendSubMenu(sub_on_top_menu, "Always on Top")
        menuBar.Append(sub_menu, "Bot Settings")
        self.SetMenuBar(menuBar)


    def launch_browser(self, evt):
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
        



    def OnStartButton(self, evt):
        """Button to start thread execution"""
        #Button to start threads
        self.stopBtn.Enable()
        self.startBtn.Disable()
        self.filterBtn.Disable()
        self.launch_threads()

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
        self.log_message_to_txt_field("Ready to start bidding process....")
        # Launch threads
        # Launch main thread and post to queue
        # Activate button to start 
        self.launchBtn.Disable()
        self.startBtn.Enable()
        self.filterBtn.Enable()


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

    def enter_login(self, evt):
        from gui_forms.logins_form import LoginFrame
        frm = LoginFrame(self, self.launcher)
        frm.Show()
        frm.ToggleWindowStyle(wx.STAY_ON_TOP)
        

    def OnFilter(self, evt):
        frm = FilterFrame(self, self.main_bot)
        frm.Show()
        


    

    
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
        self.filterBtn.Disable()
        self.stopBtn.Disable()
        self.startBtn.Disable()
        self.launchBtn.Enable()
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

#app = wx.App(redirect=True, filename="program_output")
app = wx.App(redirect=True, filename="program_output")
import locale
locale.setlocale(locale.LC_ALL, 'en_US')
frm = SharkFrame()
frm.Show()
app.MainLoop()