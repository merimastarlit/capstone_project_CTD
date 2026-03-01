from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd


# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=Options())

# helpful function copied from here:
# https://gist.github.com/toma63/c776e8f0913a656d551e0119fc7858a7
# lots more helpful selenium in that gist!
def setup_driver(headless=False):
    """Setup Chrome WebDriver with options"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=chrome_options)
    return driver


# set up our browser
# use headless if running in production!
# driver = setup_driver(headless=True)


stats = ["HR", "RBI", "SB"]

stat_map = {
    "HR": "Home Runs",
    "RBI": "Runs Batted In",
    "SB": "Stolen Bases"
}

driver = setup_driver()
all_rows = []

for year in range(2015, 2026):
    for stat in stats:
        url = f"https://www.baseball-almanac.com/yearly/top25.php?s={stat}&l=AL&y={year}"
        driver.get(url)
        display_name = stat_map[stat]
        print(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//h2[contains(text(), "{display_name}")]')))
        table = driver.find_element(
            By.XPATH, f'//h2[contains(text(), "{display_name}")]/following::table[1]')
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:  # skip header row
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 4:
                player = cells[1].text.strip()
                value = cells[2].text.strip()
                team = cells[3].text.strip()

                all_rows.append({
                    "year": year,
                    "stat_type": stat,
                    "player": player,
                    "value": value,
                    "team": team
                })


df = pd.DataFrame(all_rows)

df['value'] = pd.to_numeric(df['value'], errors="coerce")
df.dropna(subset=['value'], inplace=True)

df.to_csv("al_top25_stats_2015_2025.csv", index=False)  #


print(len(df))

print(df.head())
print(df['stat_type'].unique())
print(df['year'].unique())


# Standings

all_standings = []

for year in range(2015, 2026):

    yearly_url = f"https://www.baseball-almanac.com/yearly/yr{year}a.shtml"
    driver.get(yearly_url)

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//td[contains(@class,'banner')]"))
    )

    rows = driver.find_elements(By.TAG_NAME, "tr")

    current_division = None

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")

        if not cells:
            continue

        first_cell_class = cells[0].get_attribute("class")

        if first_cell_class and "banner" in first_cell_class:
            current_division = cells[0].text.strip()

        elif first_cell_class and "datacolBox" in first_cell_class:
            if len(cells) >= 5:
                team = cells[0].text.strip().replace(" wc", "")
                wins = cells[1].text.strip()
                losses = cells[2].text.strip()
                wp = cells[4].text.strip()

                all_standings.append({
                    "year": year,
                    "division": current_division,
                    "team": team,
                    "wins": wins,
                    "losses": losses,
                    "win_pct": wp
                })

driver.quit()

print(len(all_standings))


standings_df = pd.DataFrame(all_standings)

print(standings_df.columns)
print(len(standings_df))
print(standings_df.head())

standings_df["wins"] = pd.to_numeric(standings_df["wins"], errors="coerce")
standings_df["losses"] = pd.to_numeric(standings_df["losses"], errors="coerce")
standings_df["win_pct"] = pd.to_numeric(
    standings_df["win_pct"], errors="coerce")

standings_df.dropna(inplace=True)

standings_df.to_csv("al_standings_2015_2025.csv", index=False)
print(len(standings_df))
print(standings_df.head())
