import os
import logging
import datetime
import json
from datetime import date
from bot.bot import Bot


def start():
    # configure logging
    d = date.today()

    log_file = d.isoformat()
    log_path = os.getcwd() + "\\logs"
    print(log_path)
    logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    datefmt="'%m/%d/%Y %I:%M:%S %p",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(log_path, log_file)),
        logging.StreamHandler()
    ],
    level = logging.INFO)

    logger = logging.getLogger(__name__)

    # get posta object
    logger.info("...Starting Application...")
    logger.info("Fetching user details")
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    user_details= {}
    user_details['email'] = config['user_details']['email']
    user_details['password'] = config['user_details']['password']
    logger.info("User details fetched successfully")
    bot = Bot( user_details, logger)
    bot.start_bot()
    logger.info("Execution finished")


if __name__ == '__main__':
    start()

