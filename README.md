# Football Stats Scraper (Selenium + SQLite)

This is a custom tool I built to collect detailed football match statistics (like xG, possession, and big chances) because I couldn't find any good free datasets for my Machine Learning projects.

The script scrapes match data from Sofascore and saves it into a clean SQLite database, ready for analysis.

## 🎯 Motivation

I am interested in predicting football match outcomes using ML. However, most available datasets only show the final score (goals). To build a better model, I needed "deeper" metrics like **Expected Goals (xG)** or **Shots inside the box**.

Since this data wasn't available as a CSV, I wrote this scraper to build my own dataset.

## ⚙️ How it works

The project is built with **Python** and uses **Selenium** (specifically `undetected-chromedriver`) to navigate the website just like a real user.

### Key Features:
* **Bypasses Blocking:** Uses `undetected_chromedriver` to handle websites that block standard bots.
* **Resilient:** If the internet drops or a CAPTCHA appears, the script pauses and waits for the user instead of crashing. It also retries failed connections automatically.
* **Smart Saving:**
    * It checks if a match is already in the database before scraping to save time.
    * Match links are cached locally in JSON files so you don't have to reload the whole season list every time.
* **Structured Data:** It converts raw text from the website (e.g., "55% Ball Possession") into proper numbers and stores them in a relational database (`database.db`).

## 🛠 Libraries Used

* `selenium` & `undetected-chromedriver` - For browser automation.
* `sqlite3` - For storing data.
* `json` - For caching match links.

## 🚀 How to run

1.  **Clone the repo and install dependencies:**
    ```bash
    git clone https://github.com/GPbl3YH/football-stats-scraper.git
    cd football-stats-scraper
    pip install -r requirements.txt
    ```
    *(Note: You need Google Chrome installed)*

2.  **Start the scraper:**
    ```bash
    python main.py
    ```

3.  **Enter a season link:**
    The script will ask for a URL. You can use a link like this:
    `https://www.sofascore.com/tournament/football/england/premier-league/17#id:61627`

4.  **Check the data:**
    The script will create a file named `database.db`. You can open it with any SQLite viewer (like *DB Browser for SQLite*) to see the `matches` table.

## 📊 Data Structure

The database (`matches` table) stores data like this:

| id | date | home_team | away_team | xg_home | xg_away | possession_home | ... |
|----|------|-----------|-----------|---------|---------|-----------------|-----|
| 1 | 2023-08-12 | Arsenal | Nott. Forest | 0.85 | 1.12 | 78% | ... |

## 🚧 Future Plans

Currently, this is a pure **Data Engineering** project. My next steps are:
1.  Perform EDA (Exploratory Data Analysis) on the collected data.
2.  Train a Gradient Boosting model to predict match winners.

---
*Disclaimer: This project is for educational purposes only.*
