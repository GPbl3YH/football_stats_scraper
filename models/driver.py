import time
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import WebDriver

class Driver:
    def __init__(self, headless=True, user_agent="", proxy=None):
        self.headless = headless
        self.user_agent = user_agent
        self.proxy = proxy
        
        self.__driver = None
        
        self.start_driver()


    def start_driver(self):
        print("\n(Re)starting driver...\n")
        options = uc.ChromeOptions()

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        options.add_experimental_option("prefs", prefs)

        if self.headless: 
            options.add_argument("--headless=new")
            
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

        final_ua = self.user_agent if self.user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        options.add_argument(f'--user-agent={final_ua}')

        if self.proxy: options.add_argument(f'--proxy-server={self.proxy}')

        try:
            self.__driver = uc.Chrome(options=options, version_main=142)
            self.start_time = time.time()

        except Exception as e:
            print(f"[!] Failed to start driver: {e}")
            raise e


    def restart(self, delay=10):
        self.quit() 
        time.sleep(delay)
        self.start_driver() 


    def get_session_duration(self):
        return time.time() - self.start_time


    # Redirecting all not existed attributes to the super class (uc.Chrome)
    def __getattr__(self, name):
        if self.__driver:
            return getattr(self.__driver, name)
        
        raise AttributeError(f"Driver is not initialized or has no attribute '{name}'")
    

    def quit(self):
        if self.__driver:
            try:
                self.__driver.quit()
            except OSError:
                pass
            finally:
                self.__driver.__del__ = lambda *args, **kwargs: None
                self.__driver = None
