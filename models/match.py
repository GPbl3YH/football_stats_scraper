from common import convert_to_snake_case, PostponedError, CaptchaError
from .driver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import random
from selenium.common.exceptions import TimeoutException

class Match:
    def __init__(self, url, options, driver=None):
        self.URL = url
        if driver is None: self.DRIVER = Driver()
        else: self.DRIVER = driver


        self.DRIVER.get(self.URL)
        self.OPTIONS = convert_to_snake_case(options)
        self.STATS = {}
        self.__set_team_names()
        self.__set_match_details()
        self.__write_stats()

        if driver is None: self.DRIVER.quit()


    def __str__(self):
        return f"{self.HOME} against {self.AWAY}, leaugue: {self.LEAGUE}, stats: {self.STATS}"
    

    def __write_stats(self):
        goals = self.get_goals_in_halves()
        for half_stats, half_name in zip(self.get_match_stats(), ('FT', 'HT')):
            for stats in half_stats:
                for value, side in zip(stats[0:3:2], ('home', 'away')):
                    if stats[1] in self.OPTIONS:    #stats[1] consists of the statistic's name
                        if "%" in value:
                            try: value = max(float(value.replace('%', '')), 0.0)/100
                            except: value = 0.0
                        else:
                            value = float(value)
                        self.STATS[f'{stats[1]}_{side}_{half_name}'] = value
        
        self.STATS['goals_home_HT'] = goals[0][0]
        self.STATS['goals_away_HT'] = goals[0][1]
        self.STATS['goals_home_FT'] = goals[1][0]
        self.STATS['goals_away_FT'] = goals[1][1]


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

            # finally:
            #     time.sleep(random.uniform(0.3, 2.4))


    def get_goals_in_halves(self):
        for i in range(3):
            try:
                halves = self.DRIVER.find_elements(By.CSS_SELECTOR, "[class^='d_flex py_md px_lg gap_lg w_100%']")
                results = tuple(tuple(map(float, half.find_element(By.CSS_SELECTOR, "[class^='textStyle_display.micro c_neutrals.nLv1 ta_center d_block']").get_attribute("innerHTML").replace(h, '').split(' - '))) for half, h in zip(halves, ('FT ', 'HT ')))

                if len(results) != 0: return results[::-1]  #contains a tuple of results for HT and FT respectively
                
                if i < 2:
                    print("Error in get_goals_in_halves")
                    time.sleep(15)
                    continue
                
                raise PostponedError()
            
            except PostponedError:
                raise

            except TimeoutException as e:
                raise CaptchaError() from e

            # finally:
            #     time.sleep(random.uniform(0.3, 2.4))


    def get_match_stats(self):
        try:
            self.DRIVER.get(self.URL + ',tab:statistics')
            buttons = []
            for i in range(1, 4):
                selectors = ["tab-ALL", "tab-1ST", "tab-2ND"]
                btn = WebDriverWait(self.DRIVER, 20).until(
                    EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'[data-testid={selectors[i-1]}]')
                    )
                )
                buttons.append(btn)

            for i in range(len(buttons)):
                stat_home = WebDriverWait(self.DRIVER, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='textStyle_body.medium c_neutrals.nLv1 ta_start flex_[1_1_0px]']"))
                )

                stat_names = WebDriverWait(self.DRIVER, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='textStyle_assistive.default c_neutrals.nLv1 ta_center lc_2 px_xs']"))
                )

                stat_away = WebDriverWait(self.DRIVER, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='textStyle_body.medium c_neutrals.nLv1 ta_end flex_[1_1_0px]']"))
                )
                
                results = [[x.get_attribute('textContent'), 
                            y.get_attribute('textContent').lower().replace(' ', '_').replace('(', '').replace(')', ''),
                            z.get_attribute('textContent')] 
                            for x, y, z in zip(stat_home, stat_names, stat_away)]
                
                yield results
                
                if i < 2: self.DRIVER.execute_script("arguments[0].click();", buttons.pop(1))
        
        
        except TimeoutException as e:
                raise CaptchaError() from e

        except Exception:
            print("Error in get_match_stats")
            raise

        # finally:
        #     time.sleep(random.uniform(0.3, 2.4))


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
            
            # finally:
            #     time.sleep(random.uniform(0.3, 2.4))
            
        



