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
from sharkbot.tempBot import SharkBotTemp


        
def start():
    # set up logger
    logger = setup_logger()
    logger.info("...Starting Application...")
    logger.info("Fetching configuration details")
    
    user_details = fetch_user_details(logger)
    settings = fetch_settings(logger)
    sell_date = '2021-05-13'
    sell_date = datetime.strptime(sell_date, '%Y-%m-%d')
    expiry_date = sell_date + timedelta(200)
    if (expiry_date > datetime.now()):
        difference = expiry_date - datetime.now()
        logger.info("Executing trial version. You have %s days remaining.", difference.days)
        initialize_bots(user_details,settings, logger)
        
        """

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        executor.submit(bot_1.start_bot) 
        executor.submit(bot_2.start_bot)

        # create producer consumer bots

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(main_bot.start_bot)
            executor.submit(bot_1.start_bot)
            executor.submit(bot_2.start_bot)
        """


    else:
        logger.info("Your trial period has expired")




def initialize_bots(user_details,settings, logger):
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
    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()
    

    #executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


    # store existing orders during bot start up
    fetched_orders = main_bot.fetch_orders()
    print("Initial orders found on Ac")
    print(fetched_orders)
    main_bot.order_list.update(fetched_orders)

    # start bidding bots in seperate threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(bot_1.process_queued_orders, pipeline, event)
            executor.submit(bot_2.process_queued_orders, pipeline, event)


            # fetch new orders using main thread
            ## to do set up loop to check for new orders
            while True:
                try:                
                    new_orders = main_bot.fetch_orders()
                    queued_orders = new_orders.difference(main_bot.order_list)
                    if len(queued_orders) > 0:
                        # put urls in queue for children bidding bots
                        print(queued_orders)
                        for order in queued_orders:
                            ## add order to queue for processing
                            pipeline.put(order)
                            # add to list of processed orders
                            main_bot.order_list.add(order)
                        main_bot.driver.get("https://essayshark.com/writer/orders/")
                    else:
                        logger.info("No new orders to bid found")
                        time.sleep(main_bot.randomize_delay())
                except (KeyboardInterrupt, WebDriverException, TimeoutException):
                    print("Exiting after pressing Ctrl-C to exit")
                    logger.info("Starting the Exiting process...")
                    # signal bots to stop running
                    event.set()
                    #logger.info("Event to shutdown threads emitted")
                    # stop threads
                    #executor.shutdown(wait=True)
                    #logger.info("All threads shut down")

                    # close bots                
                    main_bot.stop_bot()
                    # loop to close children bots
                    bot_1.stop_bot()
                    bot_2.stop_bot()
                


            # close bots                
            main_bot.stop_bot()
            # loop to close children bots
            bot_1.stop_bot()
            bot_2.stop_bot()





        #queue.put(queued_orders)




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