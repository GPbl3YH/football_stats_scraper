from common import get_match_stats
from common import get_team_names
from common import Match
from common import write_stats_to_database
import sqlite3


# conn = sqlite3.connect("database.db")  
# cursor = conn.cursor()  
# cursor.execute("CREATE TABLE matches(id INTEGER PRIMARY KEY AUTOINCREMENT, home_team_name TEXT NOT NULL, away_team_name TEXT NOT NULL, ball_possession_home REAL, ball_possession_away REAL, total_shots_home INTEGER, total_shots_away INTEGER, shots_on_target_home INTEGER, shots_on_target_away INTEGER, big_chances_home INTEGER, big_chances_away INTEGER, FOREIGN KEY (home_team_name) REFERENCES teams(name) ON DELETE CASCADE, FOREIGN KEY (away_team_name) REFERENCES teams(name) ON DELETE CASCADE)"
               
               
#                )
# conn.commit()

m = Match("https://www.flashscore.com/match/football/nac-breda-nLNrHc14/twente-dhOKTHGA/?mid=CfORWml1")
write_stats_to_database(m, sqlite3.connect("database.db"))

# with open("data2.json", "w", encoding="utf-8") as f:
#     json.dump(m.stats, f, ensure_ascii=False, indent=4)




