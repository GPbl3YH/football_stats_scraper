from common import Match, Driver
from common import save_stats_to_database
from common import create_all_tables
from common import get_season_matches
import logging
import sqlite3
import time
import random


logging.basicConfig(
    filename="app.log",          # file name for logs
    level=logging.ERROR,         # logs level (ERROR and higher)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected goals (xG)', 'Shots on target', 'Ball possession', 'Big chances', 'Shots off target']
conn = sqlite3.connect("database.db")  
create_all_tables(conn, options)

laliga_22to23 = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:42409", label='LaLiga_22/23')
laliga_23to24 = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:52376", label='LaLiga_23/24')
laliga_24to25 = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:61643", label='LaLiga_24/25')


driver = Driver()
# m = Match("https://www.sofascore.com/football/match/cadiz-real-madrid/EgbsNOb#id:10408330", options, driver)
# print(m.STATS)

# driver.quit()
for season in (laliga_22to23, laliga_23to24, laliga_24to25):
    for i, match_url in enumerate(season, start=1):
        try:
            m = Match(match_url, options, driver)
            save_stats_to_database(m, conn)
            print(i, match_url)
        
        except Exception:
            message = f'Fail at {i}: {match_url}'
            logging.exception(message)
            print(message)

driver.quit()



