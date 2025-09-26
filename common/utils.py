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
                       (match.DATE, match.HOME, match.AWAY, match.STATS['full_time']['Ball possession'][0], match.STATS['full_time']['Ball possession'][1], match.STATS['full_time']['Total shots'][0], match.STATS['full_time']['Total shots'][1], match.STATS['full_time']['Shots on target'][0], match.STATS['full_time']['Shots on target'][1], match.STATS['full_time']['Big chances'][0], match.STATS['full_time']['Big chances'][1]))
    connection.commit()



def get_season_matches(url):
    driver = get_driver()
    driver.get(url)
    
    # accept_cookies(driver)
    
    drop_down_menus = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='dropdown__button dropdown__button--isOnColor_false dropdown__button--hideLabel_true']"))
    )
    driver.execute_script("arguments[0].click();", drop_down_menus[1])

    rounds = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='dropdown__listItem dropdown__listItem--isOnColor_false dropdown__listItem--hideLabel_true']"))
    )

    next_round = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='button button--variant_filled button--size_primary button--colorPalette_primary button--negative_false px_0 br_xs bg-c_surface.s2 bdr_sm']"))
    )

    links = []

    print(len(rounds))
    for x in range(len(rounds), 0, -1):
        print(x)
        is_round = driver.find_element(By.CSS_SELECTOR, 'div.dropdown__root:nth-child(2) > button:nth-child(2) > span:nth-child(1)')
        if 'Round' in is_round.get_attribute("textContent"):
            round_matches = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='sc-3f813a14-0']"))
            )
            links += [x.get_attribute("href") for x in round_matches]
        if x > 1: driver.execute_script("arguments[0].click();", next_round)

    driver.quit()
    return links, len(links)


def get_round_matches(url):
    driver = get_driver()
    driver.get(url)
    links = WebDriverWait(driver, 30).until(
          EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='sc-3f813a14-0']"))
    )
    links = [x.get_attribute("href") for x in links]

    return links


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


def get_goals_in_halves(matches, driver):
    driver.get(matches[0])

    halves = driver.find_elements(By.CSS_SELECTOR, "[class^='d_flex py_md px_lg gap_lg w_100%']")
    for half in halves:
        result = half.find_element(By.CSS_SELECTOR, "[class^='textStyle_display.micro c_neutrals.nLv1 ta_center d_block']")
        yield result.get_attribute("innerHTML")


