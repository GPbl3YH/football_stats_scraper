from common import Match
from common import save_stats_to_database
from common import create_all_tables
from common import get_season_matches, get_round_matches
from common import get_driver
import logging
import sqlite3


logging.basicConfig(
    filename="app.log",          # file name for logs
    level=logging.ERROR,         # logs level (ERROR and higher)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected goals (xG)', 'Shots on target', 'Ball possession', 'Total shots', 'Big chances', 'Shots off target']
conn = sqlite3.connect("database.db")  
create_all_tables(conn, options)

# laliga, number_of_matches = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:52376")
# print(number_of_matches)

driver = get_driver()
m = Match("https://www.sofascore.com/football/match/las-palmas-mallorca/BgbsCGc#id:11368643", options, driver)
print(m.STATS)
save_stats_to_database(m, conn)
# for i, x in zip(range(1, number_of_matches+1), laliga):
#     try:
#         m = Match(x, options, driver)
#         save_stats_to_database(m, conn)
#         print(i, x)
        
#     except Exception:
#         logging.exception(f"Fail at {i}: {x}")





