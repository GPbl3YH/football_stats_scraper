from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3


def get_match_stats(url: str, half_number=0):   #by 0 returns a full time stats
    
    assert 0 <= half_number <= 2, "Half number should be between 0 and 2"

    splitted_url = url.split("/?")  #split url into to halves to put a half number in the middle
    url =  splitted_url[0] + f"/summary/stats/{half_number}" + "/?" + splitted_url[1]
    
    """Парсинг всех значений strong[data-testid=...] через Selenium"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # скрытый режим
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        
        elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'strong[data-testid="wcl-scores-simple-text-01"]'))
        )
        values = [el.text.strip() for el in elements if el.text.strip()]
        values = list(map(list, list({tuple(values[x-3:x]) for x in range(3, len(values), 3)})))
        
        return values
    
    finally:
        driver.quit()


def get_team_names(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        
        elements = driver.find_elements(By.CSS_SELECTOR, 'a.participant__participantName')
        
        teams = {"HOME" : elements[0].text.strip(),
                 "AWAY" : elements[1].text.strip()}
        
        return teams
    
    finally:
        driver.quit()


def get_goals_in_halves(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        
        elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="wcl-scores-overline-02"] div')
        match_score = [el.text.strip() for el in elements if el.text.strip() and " - " in el.text.strip()]
        for x in range(len(match_score)):
            match_score[x] = tuple(map(int, match_score[x].split(" - ")))
        return match_score
    
    finally:
        driver.quit()

def get_league_name(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        
        elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="wcl-scores-overline-03"]')
        league_name = [el.text.strip() for el in elements if el.text.strip() and "ROUND" in el.text.strip()]
        return league_name[-1].split(" - ")[0]
    
    finally:
        driver.quit()



def write_stats_to_database(match, connection):
    cursor = connection.cursor() 

    match.write_stats()

    cursor.executemany("INSERT OR IGNORE INTO teams (name, league) VALUES (?, ?)", [(match.HOME, match.LEAGUE), (match.AWAY, match.LEAGUE)])

    cursor.execute("INSERT OR REPLACE INTO matches (home_team_name, away_team_name, ball_possession_home, ball_possession_away, total_shots_home, total_shots_away, shots_on_target_home, shots_on_target_away, big_chances_home, big_chances_away) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (match.HOME, match.AWAY, match.STATS['full_time']['Ball Possession'][0], match.STATS['full_time']['Ball Possession'][1], match.STATS['full_time']['Total shots'][0], match.STATS['full_time']['Total shots'][1], match.STATS['full_time']['Shots on target'][0], match.STATS['full_time']['Shots on target'][1], match.STATS['full_time']['Big Chances'][0], match.STATS['full_time']['Big Chances'][1]))
    connection.commit()
    connection.close()

