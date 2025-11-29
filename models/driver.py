import undetected_chromedriver as uc
import time

class Driver(uc.Chrome):
    def __init__(self, user_agent = "", proxy=None):
        options = uc.ChromeOptions()

        prefs = {
            "profile.managed_default_content_settings.images": 2,      # Картинки БЛОКИРУЕМ (безопасно)
            "profile.managed_default_content_settings.media_stream": 2, # Видео/Аудио БЛОКИРУЕМ
        }
        options.add_experimental_option("prefs", prefs)

        #options.add_argument("--headless=new") # Если ошибка останется, попробуйте временно убрать эту строку для отладки
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--disable-blink-features=AutomationControlled")

        final_ua = user_agent if user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        options.add_argument(f'--user-agent={final_ua}')

        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        super().__init__(options=options)
        self.start_time = time.time()
        

    def get_session_duration(self, current_time):
        return current_time - self.start_time


    def quit(self):
        try:
            super().quit()
        except:
            pass
