from .utils import get_match_stats, get_team_names, get_goals_in_halves, get_league_name
import sqlite3

class Match:
    
    def __init__(self, url):
        self.URL = url
        self.LEAGUE = get_league_name(url)
        self.STATS = {'first_half' : {},
                      'second_half' : {},
                      'full_time' : {}}
        teams = get_team_names(url)
        self.HOME = teams['HOME']
        self.AWAY = teams['AWAY']

    def __str__(self):
        return f"{self.HOME} against {self.AWAY}"
    
    def write_stats(self, connection):
        first_half =  get_match_stats(self.URL, 1)
        second_half = get_match_stats(self.URL, 2)
        full_time = get_match_stats(self.URL)
        goals = get_goals_in_halves(self.URL)

        for half_name, half_var in zip(['first_half', 'second_half', 'full_time'], [first_half, second_half, full_time]):
            for stats in half_var:
                if "%" in stats[0]:
                    stats[0], stats[2] = float(stats[0].strip("%"))/100, float(stats[2].strip("%"))/100
                else:
                    stats[0], stats[2] = float(stats[0]), float(stats[2])
                self.STATS[half_name][stats[1]] = (stats[0], stats[2])
        
        self.STATS['first_half']['Goals'] = goals[0]
        self.STATS['second_half']['Goals'] = goals[1]
        self.STATS['full_time']['Goals'] = [goals[0][0]+goals[1][0], goals[0][1]+goals[1][1]]




    
    
        