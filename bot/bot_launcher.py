# fetch chrome driver and settings
import json
import os
import sys
import logging
import logging.config
import json
import queue
import threading
import time
import concurrent.futures

from configparser import ConfigParser
from datetime import date, datetime, timedelta
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException



class Launcher():
    """Initializes configuration settings to run the bot"""

    def __init__(self, logger = None):
        """Initialize class and set up defaults"""
        # create logger object
        if logger is None:
            logger = self.setup_logger()
        self.logger = logger
        self.bot_settings = self.fetch_settings()
        self.user_details = self.fetch_user_details()
    
    def setup_logger(self):
        """function to set up logger"""
        # configure logging
        d = date.today()
        log_file = d.isoformat()
        ## check if file exists
        log_path = self.check_log_folder('logs')
        logging.basicConfig(format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s", datefmt="'%m/%d/%Y %I:%M:%S %p",
        handlers=[
            logging.FileHandler("{0}/{1}.log".format(log_path, log_file)),
            logging.StreamHandler()],
            level = logging.INFO)
        logger = logging.getLogger(__name__)
        return logger
    

    def check_log_folder(self,dir_name):
        """Function to ensure log directory exists"""
        if not os.path.exists(dir_name):
            try:
                os.mkdir(dir_name)
            except OSError:
                print ("[INFO] Creation of the directory {} failed".format(os.path.abspath(dir_name)))
        else:
            print ("[INFO] Successfully created the directory {} ".format(os.path.abspath(dir_name)))
        return format(os.path.abspath(dir_name))

    

    def resource_path(self, relative_path):
        """ returns correct path to chrome driver """

        try:
            base_path = sys._MEIPASS
            
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def fetch_settings(self):
        """Fetch to fetch configuration settings from setup.ini"""
        """Fetch Path to Chrome driver from config file"""
        """
        Returns settings dictionary of the form 
        settings
        ['delay':int,
        'chromedriver': string,
        'messages': [string],
        'bid_status'[Boolean],]
        """
        config = ConfigParser()
        settings = {}
        config.read("setup.ini")
        CHROME_DRIVER_PATH = config.get("chromedriver", "path")
        bid_status = config.get("bid_status","bid")
        # Fetch delay
        settings['delay']= config.getint("delay", "seconds")
        chrome_driver = self.resource_path(CHROME_DRIVER_PATH)
        self.logger.debug("Successfully fetched chrome driver path")
        # fetch client messages
        messages = json.loads(config.get("client_message","messages"))
        settings['messages'] = messages
        self.logger.info("Successfully fetched client messages")
        settings['chromedriver'] = chrome_driver
        settings['bid_status'] = bid_status
        return settings

    def fetch_user_details(self):
        """Function to fetch user details from config.json"""
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        user_details= {}
        user_details['email'] = config['user_details']['email']
        user_details['password'] = config['user_details']['password']
        self.logger.debug("User details fetched successfully")
        return user_details

    def check_expiry(self):
        """checks if trial license is valid, returns expiry date"""
        sell_date = '2021-05-13'
        sell_date = datetime.strptime(sell_date, '%Y-%m-%d')
        expiry_date = sell_date + timedelta(200)
        return expiry_date


import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msg
from tkinter import Spinbox
from datetime import date, datetime, timedelta
from sharkbot.tempBot import SharkBotTemp

class RunBot():
    def initialize_bots(self, inst):
        """Function to initialize and run bot"""
        # Initialize producer bot
        # start progress bar

        # initalize multple worker bots &
        # log in for all bots
        # Use a for loop to create a list of instances
        bots = []
        choosen_bots = int(inst.number_of_bots_chosen.get())
        i = 1
        while i <= choosen_bots:
            bot_name = "bot_" + str(i)
            bots.append(bot_name)
            i = i + 1
        inst.scrol.insert(tk.INSERT, bots)
        # start main producer bot
        inst.progress_bar.start()
        inst.main_bot = SharkBotTemp(inst.launcher.user_details,inst.launcher.bot_settings, inst.logger)
        inst.main_bot.start_bot()
        # create objects for all strings in consumer bots list
        ## To Do: Launch in a thread
        # list to hold consumer objetcs
        consumer_bots = []
        for bot in bots:
            bot = SharkBotTemp(inst.launcher.user_details,inst.launcher.bot_settings, inst.logger)
            bot.start_bot()
            consumer_bots.append(bot)

        # stop progress bar
        inst.progress_bar.stop()

        

        # pass list object to class variable for use in other functions
        inst.consumer_bots = consumer_bots
        # create event and queue
        inst.pipeline = queue.Queue(maxsize=10)
        inst.event = threading.Event()
        inst.logger.info("Queue and event object created")

        ## create producer and consumer threads
        max_workers = 5 if 5 > choosen_bots else choosen_bots
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        # creating producer thread
        # store existing orders in the main_order list
        ## store existing orders during bot start up
        fetched_orders = inst.main_bot.fetch_orders()
        inst.scrol.insert(tk.INSERT, "Initial orders found on Ac")
        inst.main_bot.order_list.update(fetched_orders)
        inst.scrol.insert(tk.INSERT, inst.main_bot.order_list)
        # launch producer thread
        self.executor.submit(inst.main_bot.fetch_queued_orders, inst.pipeline, inst.event)
        inst.logger.info("Main consumer bidding bot created and assigned to thread")

        # creating consumer thread using a for loop
        for bot in inst.consumer_bots:
            self.executor.submit(bot.process_queued_orders, inst.pipeline, inst.event)

        inst.logger.info("Producer consumer bots created")
        #inst.event.set()
