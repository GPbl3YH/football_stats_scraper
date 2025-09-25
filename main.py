from common import Match
from common import write_stats_to_database
from common import create_all_tables
from common import get_season_matches, get_round_matches
import logging
import sqlite3


logging.basicConfig(
    filename="app.log",          # file name for logs
    level=logging.ERROR,         # logs level (ERROR and higher)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected Goals (xG)', 'Shots on target', 'Ball possession', 'Total shots', 'Big chances', 'Shots off target']
conn = sqlite3.connect("database.db")  
create_all_tables(conn)

bundesliga, number_of_matches = get_season_matches("https://www.sofascore.com/tournament/football/germany/bundesliga/35#id:63516")
print(number_of_matches)


for i, x in zip(range(32, number_of_matches+1), bundesliga[31::]):
    try:
        m = Match(x, options)
        write_stats_to_database(m, conn)
        print(i, x)
    except Exception:
        logging.exception(f"Fail at {i}: {x}")




