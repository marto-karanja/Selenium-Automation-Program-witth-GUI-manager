import os
import time
import json
import random
import sys
# import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium import webdriver  
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import ElementNotVisibleException 


class Bot(object):
    """Bot class"""
    def __init__(self, user_details, settings, logger = None):
        # Set up
        self.order_list = set()
        self.email = user_details['email']
        self.password = user_details['password']
        self.logger = logger
        self.counter = 0
        #CHROME_DRIVER = os.path.join(os.path.join(os.getcwd(), 'bot\chromedriver'), 'chromedriver.exe')
        #CHROME_DRIVER = 'c:\\Users\\Admin\\Documents\\projects\\bots\\writedom\\bot\\bot\\chromedriver\\chromedriver.exe'
        CHROME_DRIVER = settings['chromedriver']
        self.BID_STATUS = settings['bid_status']
        self.DELAY = settings['delay']
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=CHROME_DRIVER)

    def randomize_delay(self):
        """Returns random delay to wait"""
        return random.randrange((int(self.DELAY/2)), self.DELAY)

    def login(self):
        self.logger.info("Logging into Shark...")
        username = self.driver.find_element_by_id('id_esauth_login_field')
        password = self.driver.find_element_by_id('id_esauth_pwd_field')
        username.send_keys(self.email)
        password.send_keys(self.password)
        signin_button  = self.driver.find_element_by_id("id_esauth_login_button")
        signin_button.click()
        self.logger.info("Completed log in process")

    def fetch_orders(self):
        """Fetch orders from tables"""
        try:
            WebDriverWait(self.driver, 240).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "order_number")))
            order_url_element = self.driver.find_elements_by_css_selector('td.order_number>a')
            order_urls = set()
            for element in order_url_element:
                order_urls.add(element.get_attribute("href"))
            self.logger.info("Fetched %s orders", len(order_urls))
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
            self.logger.info("Unable to find order table")
            # return empty set
            order_urls= ()
               
        return order_urls

    def process_orders(self,queued_orders):
        """Retrive order page and apply to the order page"""
        for order in queued_orders:
            self.logger.info("[Order %s] Fetched", order)
            #### fetch url
            self.driver.get(order)
            # get time to wait
            try:
                WebDriverWait(self.driver, 45).until(EC.visibility_of_any_elements_located((By.ID, "id_read_timeout_container")))
                time_to_wait = int(self.driver.find_element_by_id("id_read_timeout_sec").text)
                self.logger.info("Sleeping for %s secs", time_to_wait)
                time.sleep(time_to_wait+3)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
                self.logger.debug("Unable to find waiting order block")
           # order_url_element = self.driver.find_elements_by_css_selector('td.order_number>a')
            # Bid for the order
            
            ##process url
            ### get recommended bid amount
            try:
                WebDriverWait(self.driver, 240).until(EC.visibility_of_any_elements_located((By.ID, "rec_amount")))
                recommended_bid = self.driver.find_element_by_id("rec_amount").text
                # enter amount in bid amount
                bid_field = self.driver.find_element_by_id("id_bid")
                bid_field.send_keys(recommended_bid)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
                self.logger.info("Recommeded amount not found")
            else:
                """Only runs if recommended amount present"""
                # click apply button
                if (self.BID_STATUS == "True"):
                    try:
                        WebDriverWait(self.driver, 240).until( EC.element_to_be_clickable((By.ID, "apply_order")))
                        apply_button = self.driver.find_element_by_id("apply_order")
                        apply_button.click()
                        self.counter = self.counter + 1
                        self.logger.info("Applied for Order [%s]", order)
                        self.logger.info("%s orders have been processed", self.counter)
                    except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
                        self.logger.info("Apply button not found")
                
                else:
                    self.logger.info("Bid Status set to false. Order not applied")
                    self.counter = self.counter + 1
                    self.logger.info("%s orders have been processed", self.counter)

            # wait for time
            self.logger.info("Pausing execution for a few seconds...")
            #### store the applied urls in the applied orders set
            self.order_list.add(order)
            time.sleep(self.randomize_delay())


    def load_popup(self):
        """Loads the pop up form"""
        # explicitly wait for log in form button to be clickable
        try:
            WebDriverWait(self.driver, 240).until(EC.element_to_be_clickable((By.ID, "id_esauth_myaccount_login_link")))
            ##launch log in form
            login_form = self.driver.find_element_by_id("id_esauth_myaccount_login_link")
            login_form.click()
            
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
            self.logger.warning("Unable to find Log In Button")
            #exit the program
            self.stop_bot()
        else:
            # log successful presence of button
            self.logger.info("Form button ready to click")

    def enter_user_details(self):
        ### wait for form to load before entering details
        try:
            WebDriverWait(self.driver, 240).until( EC.element_to_be_clickable((By.ID, "id_esauth_login_button")))
            self.logger.info("Log in form loaded")
            
        except (ElementNotVisibleException, NoSuchElementException,TimeoutException) as e:
            self.logger.info("Unable to find log in button")
            self.logger.debug(exc_info=True)
            #exit the program
            self.stop_bot()
        else:
            # Call Log in function
            self.login()
    


        


    def start_bot(self):
        #navigate to home page  
        self.logger.info("Navigating to home page")
        self.driver.get("https://essayshark.com/")
        self.load_popup()
        self.enter_user_details()
        # enter loop to fetch orders
        try:
            while True:
                # fetch order_url
                # pause execution for a few seconds
                self.logger.info("Pausing execution for a few seconds...")
                time.sleep(self.randomize_delay())
                fetched_orders = self.fetch_orders()
                # get new orders
                queued_orders = fetched_orders.difference(self.order_list)
                # process orders
                if len(queued_orders) > 0:
                    # process queued orders
                    self.process_orders(list(queued_orders))
                    self.logger.info("Refreshing orders page")
                    self.driver.get("https://essayshark.com/writer/orders/")
                else:
                    # wait and refresh page to fetch new orders
                    self.logger.info("No new orders available to bid")
                    self.logger.info("Waiting for new orders....")
                    # implement random waits
                    time.sleep(self.randomize_delay())

        except KeyboardInterrupt:
            print("Press Ctrl-C to exit")
            self.logger.info("Exiting program...")
            self.stop_bot()
        # fetch orders after successful login
        
    


        # navigate to order page
    
    def stop_bot(self):
        """Close chrome driver and exit"""
        self.driver.quit()
        sys.exit(2)





if __name__ == "__main__":
        bot = Bot()
        bot.start_bot()