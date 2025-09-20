from common import Match
from common import write_stats_to_database
from common import create_all_tables
from common import get_season_matches
import logging
import sqlite3


logging.basicConfig(
    filename="app.log",          # имя файла для логов
    level=logging.ERROR,         # уровень логов (ERROR и выше)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected Goals (xG)', 'Shots on target', 'Ball Possession', 'Total shots', 'Big Chances', 'Shots off target']
conn = sqlite3.connect("database.db")  
create_all_tables(conn)

bundesliga, number_of_matches = get_season_matches("https://www.flashscore.com/football/germany/bundesliga-2024-2025/results/")
print(number_of_matches)


for i, x in zip(range(157,number_of_matches+1), bundesliga[156::]):
    try:
        m = Match(x, options)
        if m.LEAGUE is not None:
            write_stats_to_database(m, conn)
            print(i, x)
    except Exception:
        logging.exception(f"Fail at {i}: {x}")


# m = Match("https://www.flashscore.com/match/football/dortmund-nP1i5US1/mainz-EuakNmc1/?mid=SftwHw2E")
# print(m.LEAGUE)
# write_stats_to_database(m, conn)




