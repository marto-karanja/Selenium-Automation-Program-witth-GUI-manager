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
        self.logger.info("[Chrome Driver path]:%s", chrome_driver)
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
        sell_date = '2021-06-22'
        sell_date = datetime.strptime(sell_date, '%Y-%m-%d')
        expiry_date = sell_date + timedelta(200)
        return expiry_date


