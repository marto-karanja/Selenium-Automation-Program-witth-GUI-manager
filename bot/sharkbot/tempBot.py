# implementing explicit wait

from logging import debug, log
import time
import random
import winsound
import sys
import wx
# import webdriver 

from selenium.webdriver.chrome.options import Options 
from selenium import webdriver  
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class SharkBotTemp(object):
    def __init__(self, user_details, settings, logger = None):
        # Set up
        self.order_list = set()
        self.instatiated = True
        # counter to check how many login attempts have been made
        self.login_attempts = 0
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
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('log-level=1') 
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=CHROME_DRIVER)

    def randomize_delay(self):
        """Returns random delay to wait"""
        return random.randrange((int(self.DELAY/2)), self.DELAY)

    def login(self):
        self.logger.info("Logging into Shark...")
        try:
            WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Login')]")))
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
            self.logger.warning("Unable to find Log In Button")
        else:
            username = self.driver.find_element_by_id('auth-login')
            password = self.driver.find_element_by_id('auth-password')
            username.send_keys(self.email)
            password.send_keys(self.password)
            signin_button  = self.driver.find_element_by_xpath("//button[ @type='submit' and contains(.,'Login')]")
            signin_button.send_keys(Keys.ENTER)
            # use action chains
            """
            action = ActionChains(self.driver)
            action.click(signin_button).perform()"""
            """
            # use ACtions for click actions
            action = ActionChains(self.driver)
            action.click(signin_button).perform()"""
            #
            # 
            # signin_button.click()
            

        # Wait for login to complete
        try:
            WebDriverWait(self.driver, 45).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "order_number")))
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            self.driver.save_screenshot("Error_file.png")
            self.logger.info("Unable to find order tables: ? Log in not completed successfully")
            if self.login_attempts == 0:
                # if has not attempted to log in, try again
                self.driver.refresh()
                self.logger.info("Refreshing and attempting logon again")
                self.load_popup()
                self.login()
                self.login_attempts =  self.login_attempts + 1
        else:
            self.logger.info("Completed log in process")

    def set_filters(self, active_filters):
        filter_settings_id = {
            "sample_writing" : "id_filter_service_type_10",
            "editing_or_rewriting" : "id_filter_service_type_40",
            "writing_help" : "id_filter_service_type_400",
            "art" : "id_filter_discipline_320",
            "business_and_management": "id_filter_discipline_20",
            "computer_science" : "id_filter_discipline_110",
            "economics" : "id_filter_discipline_40",
            "engineering" : "id_filter_discipline_420",
            "english_and_literature" : "id_filter_discipline_10",
            "health_care_and_life_sciences" : "id_filter_discipline_100",
            "history" : "id_filter_discipline_50",
            "humanities" : "id_filter_discipline_430",
            "law" : "id_filter_discipline_130",
            "marketing" : "id_filter_discipline_30",
            "mathematics_and_statistics" : "id_filter_discipline_120",
            "natural_science" : "id_filter_discipline_360",
            "philosophy" : "id_filter_discipline_90",
            "political_science" : "id_filter_discipline_70",
            "psychology_and_education" : "id_filter_discipline_60",
            "religion_theology" : "id_filter_discipline_140",
            "social_science" : "id_filter_discipline_80",
            "other_disciplines" : "id_filter_discipline_10000",
            "0_8_hours" : "id_filter_deadline_1",
            "8_24_hours" : "id_filter_deadline_2",
            "1_2_days" : "id_filter_deadline_3",
            "2_3_days" : "id_filter_deadline_4",
            "3_5_days" : "id_filter_deadline_5",
            "5_7_days" : "id_filter_deadline_6",
            "7_10_days" : "id_filter_deadline_7",
            "10_days" : "id_filter_deadline_8",
            "exceeded_deadline" : "id_filter_deadline_9",
            "1_5_pages" : "id_filter_pages_1",
            "6_10_pages" : "id_filter_pages_2",
            "11_15_pages" : "id_filter_pages_3",
            "15_pages" : "id_filter_pages_4",
            "hide_viewed_orders" : "id_filter_hide_read",
            "customers_online" : "id_filter_customers_online",
            "hide_orders_placed" : "id_filter_hide_old",
            "show_outdated_orders" : "id_filter_bid_outdated",
        }
        try:
            WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "orders_list_filters_dialog_open")))
            filter_button = self.driver.find_element_by_id("orders_list_filters_dialog_open")
            filter_button.click()
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            self.driver.save_screenshot("Error_file.png")
            self.logger.info("Unable to find filter button")
    
        else:
            self.logger.info("Filter Button Clicked")
            for filter in active_filters:
                check_box = self.driver.find_element_by_id(filter_settings_id[filter])
                check_box.click()
        # click apply filter button
        apply_filter_button = self.driver.find_element_by_xpath('//*[@id="bodystart"]/div[6]/div[3]/div/button')
        apply_filter_button.click()
        try:
            WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.ID, "cancel_filter_button")))
            
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            self.driver.save_screenshot("Error_file.png")
            self.logger.info("Unable to find cancel filter button")
            return False
    
        else:
            self.logger.info("Cancel Button appeared")
            return True
        

    def page_is_loading(self):
        """Check whether page loading has completed successfully"""
        self.logger.info("Executing page is loading function")       
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            self.logger.info("Page loading has completed")
            return True
        else:
            self.logger.info("Page loading is yet to be completed")
            return False

    
    def load_popup(self):
        """Loads the pop up form"""
        # explicitly wait for log in form button to be clickable
        self.logger.info("Attempting to launch log in form pop up")
        try:
            WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.XPATH, "//button[ @type='button' and contains(.,'My account')]")))

            
            #account_button.click()
            """"
            ##launcSS_SELECTORh log in form
            login_form_button = self.driver.find_element_by_class_name("button--ghost")
            action = ActionChains(self.driver)
            action.click(login_form_button).perform()
            #login_form_button.click()"""
            
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
            self.logger.warning("Unable to find My Account Button")
            #exit the program
            #self.stop_bot()
        else:
            # log successful presence of button
            self.logger.info("Form button ready to click")
            # check if page has finished loading

            self.logger.info("Checking whether page loading has completed")
            
            page_load = self.page_is_loading()


            while not page_load:
                page_load = self.page_is_loading()
                continue

            self.logger.info("Completed checking the page load process, proceeding to click button")


            """
            Click parent
            """
            """account_button = self.driver.find_element_by_class_name("auth__block")
            x  = account_button.click()
            self.logger.info(x)"""

            # use xpath find button bt bame

            account_button = self.driver.find_element_by_xpath("//button[ @type='button' and contains(.,'My account')]")
            
            account_button.send_keys(Keys.ENTER)
   
   
            # use action chains to click
            """
            action = ActionChains(self.driver)
            action.click(account_button).perform()"""




    def enter_user_details(self):
        ### wait for form to load before entering details
        try:
            WebDriverWait(self.driver, 30).until( EC.element_to_be_clickable((By.XPATH, "//button[ @type='submit' and contains(text(),'Login')]")))
            self.logger.info("Log in form loaded")
            
        except (ElementNotVisibleException, NoSuchElementException,TimeoutException) as e:
            self.logger.info("Unable to find log in button", exc_info=True)
            #exit the program
            self.logger.info("Attempting to reclick My account button from exception code")
            #self.stop_bot()
            account_button = self.driver.find_element_by_xpath("//button[ @type='button' and contains(text(),'My account')]")
            
            account_button.send_keys(Keys.ENTER)
            # proceed to log in
            self.login()
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

    def fetch_queued_orders(self, pipeline, event, window):
        """Fetch essays urls and put in a queue"""
        self.logger.info("Looking for new orders to bid")
        while not event.isSet():
            self.logger.info("Entering the event loop")
            new_orders = self.fetch_orders()
            queued_orders = new_orders.difference(self.order_list)
            if len(queued_orders) > 0:
                # put urls in queue for children bidding bots
                print(queued_orders)
                for order in queued_orders:
                    ## add order to queue for processing
                    pipeline.put(order)
                    msg = "Order [{}] added to queue".format(order)
                    wx.CallAfter(window.log_message_to_txt_field,msg )
                    # add to list of processed orders
                    self.order_list.add(order)
                self.driver.get("https://essayshark.com/writer/orders/")
            else:
                self.logger.info("No new orders to bid found")
                time.sleep(self.randomize_delay())
                self.driver.get("https://essayshark.com/writer/orders/")


    def process_queued_orders(self,queue, event, window):
        # check for url in queue when queue is not empty
        self.logger.info("Consumer bots waiting for queue url")
        while not event.isSet() or not queue.empty():
            # get a url and start the bidding process
            self.logger.info("Child bidding bot entering loop to check if queue is populated")
            order = queue.get()
            msg = "Order [{}] added to queue".format(order)
            wx.CallAfter(window.log_message_to_txt_field, msg )
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
                        msg = "Applied for Order [{}]".format(order)
                        wx.CallAfter(window.log_message_to_txt_field, msg )
                    except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
                        self.logger.info("Apply button not found")
                    else:
                        self.chat_client()
                                       
                else:
                    self.logger.info("Bid Status set to false. Order not applied")
                    msg = "Bid Status set to false. Order [{}] not applied".format(order)
                    wx.CallAfter(window.log_message_to_txt_field, msg )
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

    def start_main_bot(self):
        """Start method for main bot"""
        #navigate to home page  
        self.logger.info("Navigating to home page")
        self.driver.get("https://essayshark.com/")
        # Log in via thread
        self.driver.refresh()
        self.logger.info("Attempting to log in")
        self.load_popup()
        
        self.enter_user_details()

        # get existing orders on page load to bid only for new orders
        fetched_orders = self.fetch_orders()
        #self.logger.debug(fetched_orders)
        self.logger.info("%s orders initially fetched", len(fetched_orders))
        # get and store initial new orders
        self.order_list.update(fetched_orders)



    def stop_bot(self):
        """Exit and clean up function"""
        self.logger.debug("Browser window exiting")
        self.driver.quit()
        #sys.exit()