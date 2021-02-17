import os
import time
import json
# import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium import webdriver  
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException 


class Bot(object):
    """Bot class"""
    def __init__(self, user_details, logger = None):
        # Set up
        self.order_list = set()
        self.email = user_details['email']
        self.password = user_details['password']
        self.logger = logger
        self.counter = 0
        #CHROME_DRIVER = os.path.join(os.path.join(os.getcwd(), 'bot\chromedriver'), 'chromedriver.exe')
        CHROME_DRIVER = 'c:\\Users\\Admin\\Documents\\projects\\bots\\writedom\\bot\\bot\\chromedriver\\chromedriver.exe'
        self.logger.info(CHROME_DRIVER)
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=CHROME_DRIVER)

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
        order_url_element = self.driver.find_elements_by_css_selector('td.order_number>a')
        order_urls = set()
        for element in order_url_element:
            order_urls.add(element.get_attribute("href"))
        self.logger.info("Fetched %s orders", len(order_urls))
        return order_urls

    def process_orders(self,queued_orders):
        """Retrive order page and apply to the order page"""
        for order in queued_orders:
            self.logger.info("[Order %s] Fetched", order)
            #### fetch url
            self.driver.get(order)
            time.sleep(145)
            ##process url
            #### store the applied urls in the applied orders set
            self.order_list.add(order)

    def start_bot(self):
        #navigate to home page  
        self.logger.info("Navigating to home page")
        self.driver.get("https://essayshark.com/")
        # explicitly wait for log in form button to be clickable
        try:
            WebDriverWait(self.driver, 240).until(EC.element_to_be_clickable((By.ID, "id_esauth_myaccount_login_link")))
            
        except (ElementNotVisibleException, NoSuchElementException) as e:
            traceback.format_exc(e)
        else:
            self.logger.info("Form button ready to click")
            """
        finally:
            self.logger.info("Closing browser execution")
            self.driver.quit()"""
        ##launch log in form
        login_form = self.driver.find_element_by_id("id_esauth_myaccount_login_link")
        login_form.click()
        ### wait for form to load before entering details
        try:
            WebDriverWait(self.driver, 240).until( EC.element_to_be_clickable((By.ID, "id_esauth_login_button")))

            
        except (ElementNotVisibleException, NoSuchElementException) as e:
            traceback.format_exc(e)
        else:
            self.logger.info("Log in form loaded")

        # Call Log in function
        self.login()
        try:
            WebDriverWait(self.driver, 240).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "order_number")))
        except (ElementNotVisibleException, NoSuchElementException) as e:
            traceback.format_exc(e)
        else:
            self.logger.info("Order table is available")
        # Fetch orders
        fetched_orders = self.fetch_orders()
        # get new orders
        queued_orders = fetched_orders.difference(self.order_list)
        # process orders
        self.process_orders(queued_orders)


        # navigate to order page





if __name__ == "__main__":
        bot = Bot()
        bot.start_bot()