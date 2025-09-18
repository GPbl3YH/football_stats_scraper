from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_all_tables(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS teams(name TEXT PRIMARY KEY, league TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS matches(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, home_team_name TEXT NOT NULL, away_team_name TEXT NOT NULL, ball_possession_home REAL, ball_possession_away REAL, total_shots_home INTEGER, total_shots_away INTEGER, shots_on_target_home INTEGER, shots_on_target_away INTEGER, big_chances_home INTEGER, big_chances_away INTEGER, FOREIGN KEY (home_team_name) REFERENCES teams(name) ON DELETE CASCADE, FOREIGN KEY (away_team_name) REFERENCES teams(name) ON DELETE CASCADE, UNIQUE(date, home_team_name, away_team_name))")
    connection.commit()           
               
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def write_stats_to_database(match, connection):
    cursor = connection.cursor() 

    cursor.executemany("INSERT OR IGNORE INTO teams (name, league) VALUES (?, ?)", [(match.HOME, match.LEAGUE), (match.AWAY, match.LEAGUE)])

    cursor.execute("INSERT OR REPLACE INTO matches (date, home_team_name, away_team_name, ball_possession_home, ball_possession_away, total_shots_home, total_shots_away, shots_on_target_home, shots_on_target_away, big_chances_home, big_chances_away) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (match.DATE, match.HOME, match.AWAY, match.STATS['full_time']['Ball Possession'][0], match.STATS['full_time']['Ball Possession'][1], match.STATS['full_time']['Total shots'][0], match.STATS['full_time']['Total shots'][1], match.STATS['full_time']['Shots on target'][0], match.STATS['full_time']['Shots on target'][1], match.STATS['full_time']['Big Chances'][0], match.STATS['full_time']['Big Chances'][1]))
    connection.commit()
    connection.close()

