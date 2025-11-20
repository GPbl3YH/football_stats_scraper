from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def convert_to_snake_case(options):
    return ['_'.join((x.replace('(', '').replace(')', '').split())).lower() for x in options]  #convert given option names to snake_case

def convert_options_to_db_columns(options):
    options_snaked = convert_to_snake_case(options=options)
    options_snaked.append('goals')   #adding goals to the list of columns. its needed to store goals scored in HT and FT, since they are not part of match statistics
    
    db_column_names = []
    for column_name in options_snaked:
        for half in ('HT', 'FT'):
            for side in ('home', 'away'):
                db_column_names.append(f'{column_name}_{side}_{half}')
    
    return db_column_names
                


def create_all_tables(connection, options):
    
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS teams(
                        name TEXT PRIMARY KEY, 
                        league TEXT NOT NULL)
                   """)
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS matches(
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   date TEXT NOT NULL,
                   home_team_name TEXT NOT NULL, 
                   away_team_name TEXT NOT NULL,
                   FOREIGN KEY (home_team_name) REFERENCES teams(name) ON DELETE CASCADE, 
                   FOREIGN KEY (away_team_name) REFERENCES teams(name) ON DELETE CASCADE, 
                   UNIQUE(date, home_team_name, away_team_name))""")
    
    cursor.execute("PRAGMA table_info(matches)")    #get meta data of all current existed columns

    current_columns = [row[1] for row in cursor.fetchall() if 'HT' in row[1] or 'FT' in row[1]] # row[1] — column name; # HT/FT are used to select only statistic columns and ignore core fields like id, home_team_name, away_team_name
    columns_from_options = convert_options_to_db_columns(options=options)

    for column_name in columns_from_options:
        if column_name not in current_columns:
            cursor.execute(f"ALTER TABLE matches ADD COLUMN {column_name} REAL")
    
    for column_name in current_columns:
        if column_name not in columns_from_options:
            cursor.execute(f"ALTER TABLE matches DROP COLUMN {column_name}")  #works only with sqlite >= 3.35
        
    connection.commit()           
               

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


def get_season_matches(url, label=""):
    from .models import Driver
    import random

    driver = Driver()
    driver.get(url)
    drop_down_menus, rounds, next_round = [], [], []

    for attempt in range(3):
        try:
            drop_down_menus = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='dropdown__button dropdown__button--isOnColor_false dropdown__button--hideLabel_true']"))
            )
            driver.execute_script("arguments[0].click();", drop_down_menus[1])

            rounds = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='dropdown__listItem dropdown__listItem--isOnColor_false dropdown__listItem--hideLabel_true']"))
            )

            next_round = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='p_xs bd_1.5px_solid_transparent bg_surface.s2 bdr_sm h_2xl w_2xl d_flex ai_center jc_center disabled:cursor_not-allowed enabled:cursor_pointer enabled:hover:bg_primary.highlight enabled:active:bg_primary.highlight enabled:focusVisible:bg_primary.highlight enabled:focusVisible:bd-c_neutrals.nLv4']"))
            )

        except Exception as e:
            print(f'Attempt {attempt} failed. Error in get_season_matches. If you see this, check the internet connection', e)
        
        # finally:
        #     time.sleep(random.uniform(0.3, 2.4))


    links = []

    print(f'Total rounds in {label}: {len(rounds)}')
    for round_number in range(len(rounds), 0, -1):
        print(round_number)
        is_round = driver.find_element(By.CSS_SELECTOR, 'div.dropdown__root:nth-child(2) > button:nth-child(2) > span:nth-child(1)')
        if 'Round' in is_round.get_attribute("textContent"):
            round_matches = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='event-hl']"))
            )
            links += [x.get_attribute("href") for x in round_matches]

        #time.sleep(random.uniform(0.3, 2.4))
        if round_number > 1: driver.execute_script("arguments[0].click();", next_round)

    driver.quit()
    return links

