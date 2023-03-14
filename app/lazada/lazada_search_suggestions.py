import json
import time
import os

import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from model.auto_suggestions_results import Result, serialize_result
from selenium.common.exceptions import NoSuchElementException


def scrape_lazada_search_suggestions(lazada_url, directory, db_url):
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    search_suggestions = db['lazada search suggestions']
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the Lazada Vietnam website
    driver.get(lazada_url)

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="q"]'))
    )

    suggestion_results = []

    search_terms = []

    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            with open(os.path.join(directory, file_name), 'r') as file:
                lines = file.read().splitlines()
                for line in lines:
                    search_terms.append(line.split(',')[0])

    site = "lazada"
    for search_term in search_terms:
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(search_term)
        time.sleep(1)
        try:
            suggestion_list = driver.find_element(By.CLASS_NAME, 'suggest-list--3Tm8')

            suggestion_keywords = [item.text for item in
                                   suggestion_list.find_elements(By.CLASS_NAME, 'suggest-common--2KmE ')]
            result = Result(site, search_term, suggestion_keywords)
            result_to_db = serialize_result(result)
            search_suggestions.update_one(
                {"keyword": result_to_db["keyword"]},
                {"$set": result_to_db},
                upsert=True
            )
            suggestion_results.append(result)
        except NoSuchElementException:
            pass


    with open("app/lazada/lazada_search_suggestions.json", "w") as file:
        json.dump(suggestion_results, file, default=serialize_result, indent=4, ensure_ascii=False)

    # Close the webdriver
    driver.quit()
