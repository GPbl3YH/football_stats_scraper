from models import Match, Driver
from common import save_stats_to_database,  create_all_tables, get_season_matches, match_exists
from common import PostponedError, CaptchaError
from selenium.common.exceptions import InvalidArgumentException
import logging
import sqlite3
import time

logging.basicConfig(
    filename="logs.log",          # file name for logs
    level=logging.ERROR,         # logs level (ERROR and higher)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

options = ['Expected goals (xG)', 'Ball possession', 'Shots on target', 'Big chances', 'Shots off target']  #<--- statistics to be saved

conn = sqlite3.connect("database.db")  
create_all_tables(conn, options)

driver = Driver()
input_message = "\nEnter a season link\n(for instance 'https://www.sofascore.com/tournament/football/england/premier-league/17#id:61627')\nand press Enter (empty input will close the programm): "
season_link = input(f"{input_message}")

while len(season_link.strip()) > 0:
    season = ""
    try:
        season = get_season_matches(season_link)

    except InvalidArgumentException:
        print("\n[!] Invalid argument. Make sure that your url is correct and try again.\n")
        season_link = input(f"{input_message}")
        continue

    except Exception as e:
        print(e)

    i = 0
    reconnection_attempt = 0
    general_retry_count = 0

    while i < len(season):
        match_url = season[i]
        try:
            if match_exists(match_url, conn):
                print(f"{i+1}) {match_url} already exists [*]")
                i+=1
                continue

            m = Match(match_url, options, driver)
            save_stats_to_database(m, conn)
            print(f"{i+1}) {match_url} successfully added [+]")

        except PostponedError as e:
            message = f"[!] Postponed at {i+1}: {type(e)}\n{e}\n"
            logging.exception(message)
            print(message)

        except CaptchaError as e:
            message = f"[!] CAPTCHA at {i+1}: {type(e)}\n{e}\n"
            logging.exception(message)
            print(message)

            input(
                "\nConnect to a mobile hotspot. If already connected, cycle Airplane Mode (on/off) "
                "to reset the connection.\nWait 10-15s before reconnecting.\n"
                "Press Enter to continue...\n"
            )
            reconnection_attempt += 1

            if reconnection_attempt > 3:
                raise Exception()
            
            print(f"\nReconnection attempt: {reconnection_attempt}/3\n")

            time.sleep(10)
            driver.restart()

            continue

        except Exception as e:
            message = f'\nGeneral error at {i+1}: {match_url} occured\n'
            logging.exception(message)
            print(message)
            
            driver.restart()
            reconnection_attempt = 0 

            if general_retry_count == 0:
                print("First error on this match. Retrying...")
                general_retry_count += 1
                continue

            else:
                print("Second error on this match. Skipping to next...")
                general_retry_count = 0 
                reconnection_attempt = 0

        i += 1

        if driver.get_session_duration() > 300:  #restart driver every 5 minutes
            driver.restart()

    season_link = input("\n\nEnter an another link and press Enter (or just leave it empty to finish): ")

driver.quit()


