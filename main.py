from common import Match
from common import write_stats_to_database
from common import create_all_tables
import sqlite3


conn = sqlite3.connect("database.db")  
create_all_tables(conn)

m = Match("https://www.flashscore.com/match/football/como-ttyLthOA/lazio-URcSl02h/?mid=SvxXQBaf")
write_stats_to_database(m, conn)




