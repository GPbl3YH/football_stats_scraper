import time
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def safe_del(self):
    try:
        self.quit()
    except OSError:
        pass
    except Exception:
        pass

uc.Chrome.__del__ = safe_del    # Adding destructor to undetected_chromedriver.Chrome to properly close the driver


class Driver:
    def __init__(self, headless=True, user_agent="", proxy=None):
        self.headless = headless
        self.user_agent = user_agent
        self.proxy = proxy
        
        self.__driver = None
        self.modals_closed = False

        self.start_driver()
        self.close_all_modals()


    def start_driver(self):
        print("\n(Re)starting driver...\n")
        options = uc.ChromeOptions()

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            "profile.default_content_setting_values.notifications": 2,
            "intl.accept_languages": "en-US,en"
            }
        
        options.add_experimental_option("prefs", prefs)

        if self.headless: 
            options.add_argument("--headless=new")
            
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

        final_ua = self.user_agent if self.user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7680.165 Safari/537.36"
        options.add_argument(f'--user-agent={final_ua}')

        self.modals_closed = False

        if self.proxy: options.add_argument(f'--proxy-server={self.proxy}')
        
        try:
            self.__driver = uc.Chrome(options=options, version_main=146)
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


    def close_all_modals(self, timeout=2):
        if self.__driver.title in ["Neuer Tab", "New Tab"]:
            return False
        
        common_cookie_selectors = [
            "body > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button",
            "#portals > div.ui-modal.modalRecipe__overlay.modalRecipe__overlay--overlayZIndex_default.modalRecipe__overlay--blurBackground_false > div > div > div.d_flex.jc_space-between.gap_sm.p_lg.pt_sm > button"
            ]
        
        for selector in common_cookie_selectors:
            try:
                wait = WebDriverWait(self.__driver, timeout)
                button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                self.__driver.execute_script("arguments[0].click();", button)
                
                print(f"[++] Modal found and clicked: {selector}")
                
            except Exception:
                continue
                
        return True
                

    def get(self, url):
        self.__driver.get(url)

        if not self.modals_closed:
            self.modals_closed = self.close_all_modals()

                
    # Redirecting all not existed attributes to the super class (uc.Chrome)
    def __getattr__(self, name):
        if self.__driver:
            return getattr(self.__driver, name)
        
        raise AttributeError(f"Driver is not initialized or has no attribute '{name}'")
    