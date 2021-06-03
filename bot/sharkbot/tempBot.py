# implementing explicit wait

from logging import debug
import time
import random
import winsound
import sys
# import webdriver 

from selenium.webdriver.chrome.options import Options 
from selenium import webdriver  
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.common.exceptions import ElementNotVisibleException 


class SharkBotTemp(object):
    def __init__(self, user_details, settings, logger = None):
        # Set up
        self.order_list = set()
        self.email = user_details['email']
        self.password = user_details['password']
        self.logger = logger
        self.logger.info("Initializing browser instance")
        self.counter = 0
        # message list
        self.message_list = settings['messages']
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

    def wait_for_new_orders(self):
        # wait for new orders as they appear in home page
        # set up loop
        try:
            while True:
                # check for new orders
                fetched_orders = self.fetch_orders()
                # check for new orders from processed orders
                queued_orders = fetched_orders.difference(self.order_list)
                self.logger.info("%s new orders found", len(queued_orders))
                if len(queued_orders) > 0:
                    self.process_orders(queued_orders)
                    self.driver.get("https://essayshark.com/writer/orders/")
                else:
                    time.sleep(self.randomize_delay())
        except KeyboardInterrupt:
            print("Press Ctrl-C to exit")
            self.logger.info("Exiting program...")
            self.stop_bot()
    

        

    def fetch_orders(self):
        """Fetch all orders available from tables"""
        try:
            WebDriverWait(self.driver, 240).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "order_number")))
            order_url_element = self.driver.find_elements_by_css_selector('td.order_number>a')
            order_urls = set()
            for element in order_url_element:
                order_urls.add(element.get_attribute("href"))
            self.logger.debug("Fetched %s orders", len(order_urls))
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            self.driver.save_screenshot("Error_file.png")
            self.logger.info("Unable to find order table")
            self.driver.refresh()
            # return empty set
            order_urls= ()
        return order_urls

    def process_queued_orders(self,queue, event):
        # check for url in queue when queue is not empty
        while not event.is_set() or not queue.empty():
            # get a url and start the bidding process
            order = queue.get()
            self.logger.info("Consumer Bidding bot applyin for url: %s (size=%d)", order, queue.qsize())
            #### fetch url
            self.driver.get(order)
            # get time to wait
            try:
                WebDriverWait(self.driver, 45).until(EC.visibility_of_any_elements_located((By.ID, "id_read_timeout_container")))
                time_to_wait_element = self.driver.find_element_by_id("id_read_timeout_sec")
                if (time_to_wait_element.is_displayed()):
                    time_to_wait = int(time_to_wait_element.text)
                    self.logger.info("Sleeping for %s secs", time_to_wait)
                    time.sleep(time_to_wait)
                # check if file download is required
                file_check= self.driver.find_element_by_id("id_read_files_msg_container").is_displayed()
                if file_check:
                    self.download_files()

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
                        self.chat_client()
                                       
                else:
                    self.logger.info("Bid Status set to false. Order not applied")
                    self.counter = self.counter + 1
                    self.logger.info("%s orders have been processed", self.counter)


        
    def process_orders(self,queued_orders):
        """Bid for order and talk to customer"""
        for order in queued_orders:
            self.logger.info("[Order %s] Fetched", order)
            #### fetch url
            self.driver.get(order)
            # get time to wait
            try:
                WebDriverWait(self.driver, 45).until(EC.visibility_of_any_elements_located((By.ID, "id_read_timeout_container")))
                time_to_wait_element = self.driver.find_element_by_id("id_read_timeout_sec")
                if (time_to_wait_element.is_displayed()):
                    time_to_wait = int(time_to_wait_element.text)
                    self.logger.info("Sleeping for %s secs", time_to_wait)
                    time.sleep(time_to_wait)
                # check if file download is required
                file_check= self.driver.find_element_by_id("id_read_files_msg_container").is_displayed()
                if file_check:
                    self.download_files()

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
                        self.chat_client()
                                       
                else:
                    self.logger.info("Bid Status set to false. Order not applied")
                    self.counter = self.counter + 1
                    self.logger.info("%s orders have been processed", self.counter)
                    


        #### store the applied urls in the applied orders set
        self.order_list.add(order)
        self.logger.info("URL processed")
        self.counter = self.counter + 1
        self.logger.info("%s orders processed", self.counter)

    def download_files(self):
        """Download files if required"""
        file_block = self.driver.find_elements_by_css_selector('.paper_instructions_view>a')
        file_urls = []
        for url in file_block:
             file_urls.append(url.get_attribute("href"))
        counter = 0
        for url in file_urls:
            if 'https://essayshark.com/writer/get_additional_material.html?' in url:
                self.driver.get(url)
                counter = counter + 1
            if counter > 1:
                break
        self.logger.info("%s files downloaded", counter)


    def chat_client(self):
        # beep to alert message
        try:
            WebDriverWait(self.driver, 240).until(EC.visibility_of_any_elements_located((By.ID, "id_body")))
            # enter message in client chat
            customer_chat_box = self.driver.find_element_by_id("id_body")
            chat_box_button = self.driver.find_element_by_id("id_send_message")
            customer_chat_box.send_keys(self.message_list[(random.randrange(0, len(self.message_list)))])
            # send message by clicking send button
            chat_box_button.click()
            # wait for time
            #winsound.Beep(440, 3000)
            self.logger.info("Message sent to client")
            self.logger.info("Pausing execution for a few seconds...")
            time.sleep(self.randomize_delay())
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
            self.driver.save_screenshot("error_file.png")



    def start_bot(self):
        #navigate to home page  
        self.logger.info("Navigating to home page")
        self.driver.get("https://essayshark.com/")
        # Log in via thread
        self.logger.info("Attempting to log in")
        self.load_popup()
        
        self.enter_user_details()
        # set up loop to keep browser window open indefinetly
        """
        try:
            while True:
               print("Waiting for input from Queue")
               #time.sleep(random.randrange(self.DELAY, 25))
                    
        except KeyboardInterrupt:
            print("Press Ctrl-C to exit")
            self.logger.info("Exiting program...")
            self.stop_bot()"""
        """
        self.driver.get("https://essayshark.com/")

        # get existing orders
        fetched_orders = self.fetch_orders()
        self.logger.debug(fetched_orders)
        self.logger.info("%s orders initially fetched", len(fetched_orders))
        # get new orders
        self.order_list.update(fetched_orders)
        # wait for new orders
        self.wait_for_new_orders()"""



    def stop_bot(self):
        """Exit and clean up function"""
        self.logger.debug("Browser window exiting")
        self.driver.quit()
        sys.exit()