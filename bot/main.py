# fetch chrome driver and settings
import json
import os
import sys
import logging
import logging.config
import json
import time
import imaplib
import email
from configparser import ConfigParser
from datetime import date, datetime, timedelta
from sharkbot.bot import SharkBot

def start():
    # set up logger
    logger = setup_logger()
    logger.info("...Starting Application...")
    logger.info("Fetching configuration details")
    
    user_details = fetch_user_details(logger)
    settings = fetch_settings(logger)
    sell_date = '2021-05-13'
    sell_date = datetime.strptime(sell_date, '%Y-%m-%d')
    expiry_date = sell_date + timedelta(20)
    if (expiry_date > datetime.now()):
        difference = expiry_date - datetime.now()
        logger.info("Executing trial version. You have %s days remaining.", difference.days)
        bot = SharkBot(user_details,settings, logger)
        bot.start_bot()

    else:
        logger.info("Your trial period has expired")





def setup_logger():
    """function to set up logger"""
    # configure logging
    d = date.today()

    log_file = d.isoformat()
    ## check if file exists    
    log_path = check_log_folder('logs')
    logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    datefmt="'%m/%d/%Y %I:%M:%S %p",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(log_path, log_file)),
        logging.StreamHandler()
    ],
    level = logging.INFO)

    logger = logging.getLogger(__name__)
    return logger
    

def check_log_folder(dir_name):
    """Function to ensure log directory exists"""
    if not os.path.exists(dir_name):
        try:
            os.mkdir(dir_name)
        except OSError:
            print ("[INFO] Creation of the directory {} failed".format(os.path.abspath(dir_name)))
    else:
        print ("[INFO] Successfully created the directory {} ".format(os.path.abspath(dir_name)))
    return format(os.path.abspath(dir_name))

def resource_path(logger, relative_path):

    try:
        base_path = sys._MEIPASS
        
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def fetch_settings(logger):
    """Fetch to fetch configuration settings from setup.ini"""
    """Fetch Path to Chrome driver from config file"""
    config = ConfigParser()
    settings = {}
    config.read("setup.ini")
    CHROME_DRIVER_PATH = config.get("chromedriver", "path")
    bid_status = config.get("bid_status","bid")
    # Fetch delay
    settings['delay']= config.getint("delay", "seconds")
    chrome_driver = resource_path(logger, CHROME_DRIVER_PATH)
    logger.debug("Successfully fetched chrome driver path")
    # fetch client messages
    messages = json.loads(config.get("client_message","messages"))
    settings['messages'] = messages
    logger.info("Successfully fetched client messages")
    settings['chromedriver'] = chrome_driver
    settings['bid_status'] = bid_status
    return settings

def fetch_user_details(logger):
    """Function to fetch user details from config.json"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    user_details= {}
    user_details['email'] = config['user_details']['email']
    user_details['password'] = config['user_details']['password']
    logger.debug("User details fetched successfully")
    return user_details

if __name__ == '__main__':
    start()