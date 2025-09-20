from .utils import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time


class Match:
    
    def __init__(self, url, options):
        self.URL = url
        self.DRIVER = get_driver()
        self.DRIVER.get(self.URL)
        self.OPTIONS = options

        self.__set_match_date()
        self.__set_team_names()
        self.__set_league_name()
        self.STATS = {'first_half' : {},
                      'second_half' : {},
                      'full_time' : {}}
        self.write_stats()
        self.DRIVER.quit()

    def __str__(self):
        return f"{self.HOME} against {self.AWAY}, leaugue: {self.LEAGUE}, stats: {self.STATS}"
    
    def write_stats(self):
        goals = self.get_goals_in_halves()
        first_half =  self.get_match_stats(1)
        second_half = self.get_match_stats(2)
        full_time = self.get_match_stats()

        for half_name, half_var in zip(['first_half', 'second_half', 'full_time'], [first_half, second_half, full_time]):
            for stats in half_var:
                if stats[1] in self.OPTIONS:
                    if "%" in stats[0] or "%" in stats[2]:
                        stats0, stats1 = stats[0].split("%")[0], stats[2].split("%")[0]
                        try: stats[0] = max(float(stats0), 0.0)/100
                        except: stats[0] = 0.0
                        try: stats[2] = max(float(stats1), 0.0)/100
                        except: stats[2] = 0.0
                    else:
                        stats[0], stats[2] = float(stats[0]), float(stats[2])
                    self.STATS[half_name][stats[1]] = (stats[0], stats[2])
        
        self.STATS['first_half']['Goals'] = goals[0]
        self.STATS['second_half']['Goals'] = goals[1]
        self.STATS['full_time']['Goals'] = tuple([goals[0][0]+goals[1][0], goals[0][1]+goals[1][1]])

        self.DRIVER.quit()

    def __set_team_names(self):

        while True:
            try:
                elements = self.DRIVER.find_elements(By.CSS_SELECTOR, 'a.participant__participantName')
            
                self.HOME = elements[0].text.strip()
                self.AWAY = elements[1].text.strip()
                break

            except Exception:
                print("Error in __set_team_names")
                time.sleep(1)


    def get_goals_in_halves(self):

        while True:
            try:
                elements = WebDriverWait(self.DRIVER, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="wcl-scores-overline-02"] div'))
                )
                match_score = [el.text.strip() for el in elements if el.text.strip() and " - " in el.text.strip()]
                for x in range(len(match_score)):
                    match_score[x] = tuple(map(int, match_score[x].split(" - ")))

                if len(match_score) != 0:
                    return match_score
                
                raise Exception
            
            except:
                print("Error in get_goals_in_halves")
                time.sleep(1)
    
    def get_match_stats(self, half_number=0):   #by 0 returns a full time stats
        assert 0 <= half_number <= 2, "Half number should be between 0 and 2"
        
        splitted_url = self.URL.split("/?") #split url into to halves to put a half number in the middle
        updated_url =  splitted_url[0] + f"/summary/stats/{half_number}" + "/?" + splitted_url[1]
        
        try:
            self.DRIVER.get(updated_url)
            
            elements = WebDriverWait(self.DRIVER, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'strong[data-testid="wcl-scores-simple-text-01"]'))
            )
            values = [el.text.strip() for el in elements if el.text.strip()]
            values = list(map(list, list({tuple(values[x-3:x]) for x in range(3, len(values), 3)})))
            
            return values
        
        finally:
            pass


    def __set_match_date(self):

        while True:
            try:

                element = self.DRIVER.find_element(By.CSS_SELECTOR, 'div.duelParticipant__startTime > div') #returns Day.Month.Year Hours:Minutes

                match_date = datetime.strptime(element.text.strip(), "%d.%m.%Y %H:%M").date() #leaves only a date
                
                self.DATE = match_date
                break
            
            except Exception:
                print("Error in __set_match_date")
                time.sleep(1)


    def __set_league_name(self):
        try:
            elements = self.DRIVER.find_elements(By.CSS_SELECTOR, 'span[data-testid="wcl-scores-overline-03"]')
            league_name = [el.text.strip() for el in elements if el.text.strip() and "ROUND" in el.text.strip()]

            if (len(league_name)) != 0:
                self.LEAGUE = league_name[-1].split(" - ")[0]
            
            else:
                self.LEAGUE = None

        finally:
            pass

            