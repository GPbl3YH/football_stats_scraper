from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def convert_to_snake_case(options):
    return ['_'.join((x.replace('(', '').replace(')', '').split())).lower() for x in options]  #convert given option names to snake_case


def create_all_tables(connection, options):
    db_column_names = convert_to_snake_case(options=options)
    db_column_names.append('goals')   #adding goals to the list of columns. its needed to store goals scored in HT and FT, since they are not part of match statistics

    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS teams(
                        name TEXT PRIMARY KEY, 
                        league TEXT NOT NULL)
                   """)
    #TODO: delete rows which are not in options anymore
    cursor.execute("""CREATE TABLE IF NOT EXISTS matches(
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   date TEXT NOT NULL,
                   home_team_name TEXT NOT NULL, 
                   away_team_name TEXT NOT NULL,
                   goals_home_HT REAL,
                   goals_away_HT REAL,
                   goals_home_FT REAL,
                   goals_away_FT REAL,
                   FOREIGN KEY (home_team_name) REFERENCES teams(name) ON DELETE CASCADE, 
                   FOREIGN KEY (away_team_name) REFERENCES teams(name) ON DELETE CASCADE, 
                   UNIQUE(date, home_team_name, away_team_name))""")
    
    cursor.execute("PRAGMA table_info(matches)")    #get meta data of all columns
    columns = [row[1] for row in cursor.fetchall()] # row[1] — column name
    print(columns)

    for column_name in db_column_names:
        try:
            cursor.execute(f"ALTER TABLE matches ADD COLUMN {column_name}_home_HT REAL")
            cursor.execute(f"ALTER TABLE matches ADD COLUMN {column_name}_away_HT REAL")
            cursor.execute(f"ALTER TABLE matches ADD COLUMN {column_name}_home_FT REAL")
            cursor.execute(f"ALTER TABLE matches ADD COLUMN {column_name}_away_FT REAL")
        except Exception as e:
            if "duplicate column name" in e.args[0]:
                print("duplicate")


        
    connection.commit()           
               
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080") 
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def save_stats_to_database(match, connection):

    cursor = connection.cursor() 

    cursor.executemany("INSERT OR IGNORE INTO teams (name, league) VALUES (?, ?)", [(match.HOME, match.LEAGUE), (match.AWAY, match.LEAGUE)])
    
    
    data = {
    "date": match.DATE,
    "home_team_name": match.HOME,
    "away_team_name": match.AWAY,
    **match.STATS
    }

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    values = tuple(data.values())

    sql_request = f"INSERT OR REPLACE INTO matches ({columns}) VALUES ({placeholders})"
    cursor.execute(sql_request, values)
    connection.commit()


def get_season_matches(url):
    driver = get_driver()
    driver.get(url)
    
    drop_down_menus = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='dropdown__button dropdown__button--isOnColor_false dropdown__button--hideLabel_true']"))
    )
    driver.execute_script("arguments[0].click();", drop_down_menus[1])

    rounds = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='dropdown__listItem dropdown__listItem--isOnColor_false dropdown__listItem--hideLabel_true']"))
    )

    next_round = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='p_xs bd_1.5px_solid_transparent bg_surface.s2 bdr_sm h_2xl w_2xl d_flex ai_center jc_center disabled:cursor_not-allowed enabled:cursor_pointer enabled:hover:bg_primary.highlight enabled:active:bg_primary.highlight enabled:focusVisible:bg_primary.highlight enabled:focusVisible:bd-c_neutrals.nLv4']"))
    )

    links = []

    print(len(rounds))
    for x in range(len(rounds), 0, -1):
        print(x)
        is_round = driver.find_element(By.CSS_SELECTOR, 'div.dropdown__root:nth-child(2) > button:nth-child(2) > span:nth-child(1)')
        if 'Round' in is_round.get_attribute("textContent"):
            round_matches = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='event-hl']"))
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


def get_goals_in_halves(matches, driver):
    driver.get(matches[0])

    halves = driver.find_elements(By.CSS_SELECTOR, "[class^='d_flex py_md px_lg gap_lg w_100%']")
    for half in halves:
        result = half.find_element(By.CSS_SELECTOR, "[class^='textStyle_display.micro c_neutrals.nLv1 ta_center d_block']")
        yield result.get_attribute("innerHTML")


