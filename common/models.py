from .utils import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time


class Match:
    
    def __init__(self, url, options, driver=None):
        self.URL = url
        if driver is None: self.DRIVER = get_driver()
        else: self.DRIVER = driver


        self.DRIVER.get(self.URL)
        self.OPTIONS = options
        self.STATS = {'full_time' : {},
                      'first_half' : {},
                      'second_half' : {}}
        
        self.__set_team_names()
        self.__set_match_details()
        self.__write_stats()

        if driver is None: self.DRIVER.quit()

    def __str__(self):
        return f"{self.HOME} against {self.AWAY}, leaugue: {self.LEAGUE}, stats: {self.STATS}"
    
    def __write_stats(self):
        goals = self.get_goals_in_halves()
        for half_stats, half_name in zip(self.get_match_stats(), self.STATS.keys()):
            for stats in half_stats:
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
        self.STATS['second_half']['Goals'] = tuple([goals[1][0]-goals[0][0], goals[1][1]-goals[0][1]])
        self.STATS['full_time']['Goals'] = goals[1]

    def __set_team_names(self):

        for _ in range(3):
            try:
                elements = self.DRIVER.find_elements(By.CSS_SELECTOR, "[class*='textStyle_display.medium c_neutrals.nLv1 max-w_[100px] md:max-w_8xl lg:max-w_[156px] trunc_true d_block ta_start']")
            
                self.HOME = elements[0].get_attribute("textContent").strip()
                self.AWAY = elements[1].get_attribute("textContent").strip()

                break

            except Exception:
                print("Error in __set_team_names")
                time.sleep(1)


    def get_goals_in_halves(self):

        for _ in range(3):
            try:

                halves = self.DRIVER.find_elements(By.CSS_SELECTOR, "[class^='d_flex py_md px_lg gap_lg w_100%']")
                results = tuple(tuple(map(int, half.find_element(By.CSS_SELECTOR, "[class^='textStyle_display.micro c_neutrals.nLv1 ta_center d_block']").get_attribute("innerHTML").replace(h, '').split(' - '))) for half, h in zip(halves, ('FT ', 'HT ')))

                return results[::-1]  #contains a tuple of results for HT and FT respectively
                
            except:
                print("Error in get_goals_in_halves")
                time.sleep(1)
    
    def get_match_stats(self):

        try:
            self.DRIVER.get(self.URL + ',tab:statistics')
            buttons = WebDriverWait(self.DRIVER, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='Chip kkEtZp']"))
                    )
            
            for i in range(3):
                stats_with_percents = WebDriverWait(self.DRIVER, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='Text gxbNET']"))
                )

                stat_home = WebDriverWait(self.DRIVER, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='Text iZtpCa']"))
                )

                stat_names = WebDriverWait(self.DRIVER, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='Text lluFbU']"))
                )

                stat_away = WebDriverWait(self.DRIVER, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='Text lfzhVF']"))
                )

                for x in range(len(stat_names)):
                    if stat_names[x].get_attribute('textContent') in ['Ball possession', 'Duels']:
                        stat_home.insert(x, stats_with_percents.pop(0))
                        stat_away.insert(x, stats_with_percents.pop(0))
                

                results = [[x.get_attribute('textContent'), y.get_attribute('textContent'), z.get_attribute('textContent')] for x, y, z in zip(stat_home, stat_names, stat_away)]
                
                yield results
                
                if i < 2: self.DRIVER.execute_script("arguments[0].click();", buttons.pop(0))
               

        
        finally:
            pass


    def __set_match_details(self):

        for _ in range(3):
            try:
                elements = self.DRIVER.find_elements(By.CSS_SELECTOR, "[class*='textStyle_display.micro c_neutrals.nLv3']") #returns date of match, start time, league name and field's name
                elements = [x.get_attribute("textContent").strip() for x in elements]

                match_date = datetime.strptime(elements[0], "%d/%m/%Y").date().isoformat()

                self.DATE = match_date
                self.LEAGUE = elements[2]
                break
            
            except Exception:
                print("Error in __set_match_date")
                time.sleep(1)


            