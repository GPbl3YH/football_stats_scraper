from common import Match
from common import save_stats_to_database
from common import create_all_tables
from common import get_season_matches
from common import get_driver
import logging
import sqlite3


logging.basicConfig(
    filename="app.log",          # file name for logs
    level=logging.ERROR,         # logs level (ERROR and higher)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected goals (xG)', 'Shots on target', 'Ball possession', 'Big chances', 'Shots off target']
conn = sqlite3.connect("database.db")  
create_all_tables(conn, options)

laliga, number_of_matches = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:52376")
print(f'Total matches: {number_of_matches}')

driver = get_driver()

for i, match_url in enumerate(laliga, start=1):
    try:
        m = Match(match_url, options, driver)
        save_stats_to_database(m, conn)
        print(i, match_url)

    except Exception:
        logging.exception(f'Fail at {i}: {match_url}')





