from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def create_all_tables(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS teams(name TEXT PRIMARY KEY, league TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS matches(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, home_team_name TEXT NOT NULL, away_team_name TEXT NOT NULL, ball_possession_home REAL, ball_possession_away REAL, total_shots_home INTEGER, total_shots_away INTEGER, shots_on_target_home INTEGER, shots_on_target_away INTEGER, big_chances_home INTEGER, big_chances_away INTEGER, FOREIGN KEY (home_team_name) REFERENCES teams(name) ON DELETE CASCADE, FOREIGN KEY (away_team_name) REFERENCES teams(name) ON DELETE CASCADE, UNIQUE(date, home_team_name, away_team_name))")
    connection.commit()           
               
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080") 
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def write_stats_to_database(match, connection):
    cursor = connection.cursor() 

    cursor.executemany("INSERT OR IGNORE INTO teams (name, league) VALUES (?, ?)", [(match.HOME, match.LEAGUE), (match.AWAY, match.LEAGUE)])

    cursor.execute("INSERT OR REPLACE INTO matches (date, home_team_name, away_team_name, ball_possession_home, ball_possession_away, total_shots_home, total_shots_away, shots_on_target_home, shots_on_target_away, big_chances_home, big_chances_away) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (match.DATE, match.HOME, match.AWAY, match.STATS['full_time']['Ball Possession'][0], match.STATS['full_time']['Ball Possession'][1], match.STATS['full_time']['Total shots'][0], match.STATS['full_time']['Total shots'][1], match.STATS['full_time']['Shots on target'][0], match.STATS['full_time']['Shots on target'][1], match.STATS['full_time']['Big Chances'][0], match.STATS['full_time']['Big Chances'][1]))
    connection.commit()



def get_season_matches(url):
    driver = get_driver()
    driver.get(url)
    driver.save_screenshot("screenshot1.png")
    
    accept_cookies(driver)
    
    try:
        while True:
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".wclButtonLink"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)

    except Exception as e:
        print("The button is disappeared")

    finally:
        pass

    elements = driver.find_elements(By.CLASS_NAME, 'eventRowLink')
    links = [''.join(x.get_attribute("href").split("/summary")) for x in elements]

    driver.quit()
    return links, len(links)


def accept_cookies(driver):
    try:
        # Ждём появления iframe (если он есть)
        iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#onetrust-banner-sdk"))
        )
        driver.switch_to.frame(iframe)
        print("in iframe")
    except:
        print("iframe wasnt found")
        iframe = None

    try:
        # Ждём кнопку
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        # Пробуем кликнуть через JS (надёжнее, чем обычный click)
        driver.execute_script("arguments[0].click();", accept_btn)
        print("Cookies accepted")
    except:
        print("'I Accept' wasnt found")

    if iframe:
        driver.switch_to.default_content()  # возвращаемся в основной DOM
    time.sleep(1)  # небольшая пауза, чтобы страница обновилась


