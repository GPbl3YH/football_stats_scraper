from models import Match, Driver
from common import save_stats_to_database
from common import create_all_tables
from common import get_season_matches
import logging
import sqlite3


logging.basicConfig(
    filename="logs.log",          # file name for logs
    level=logging.ERROR,         # logs level (ERROR and higher)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected goals (xG)', 'Ball possession', 'Shots on target', 'Big chances', 'Shots off target']
conn = sqlite3.connect("database.db")  
create_all_tables(conn, options)

# laliga_22to23 = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:42409", label="LaLiga 2022/2023")
# laliga_23to24 = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:52376", label="LaLiga 2023/2024")
# laliga_24to25 = get_season_matches("https://www.sofascore.com/tournament/football/spain/laliga/8#id:61643", label="LaLiga 2024/2025")

driver = Driver()
m = Match("https://www.sofascore.com/football/match/las-palmas-mallorca/BgbsCGc#id:11368643", options, driver)
print(m.STATS)
save_stats_to_database(m, conn)

# print(len(laliga_22to23), len(laliga_23to24), len(laliga_24to25))

# for season in (laliga_22to23, laliga_23to24, laliga_24to25):
#     for i, match_url in enumerate(season, start=1):
#         try:
#             m = Match(match_url, options, driver)
#             save_stats_to_database(m, conn)
#             print(i, match_url)
        
#         except Exception:
#             message = f'Fail at {i}: {match_url}'
#             logging.exception(message)
#             print(message)

driver.quit()



