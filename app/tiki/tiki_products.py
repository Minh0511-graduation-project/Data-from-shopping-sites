import json
import time
import os
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from model.auto_suggestions_results import Result
from selenium.webdriver.common.keys import Keys


def scrape_tiki_products(tiki_url, directory):
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the Tiki Vietnam website
    driver.get(tiki_url)

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Bạn tìm gì hôm nay"]'))
    )

    with open('app/tiki/tiki.json') as f:
        data = json.load(f)

    # get all the suggestions and store it in an array
    search_suggestions = []
    for _, e in enumerate(data):
        search_suggestions.append(e['suggestions'])

    # flatten the array
    search_suggestions = [item for sublist in search_suggestions for item in sublist]

    for suggestion in search_suggestions:
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(suggestion)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(3)
        best_seller = driver.find_element(By.XPATH, '//a[contains(text(),"Bán chạy")]')
        best_seller.click()
        time.sleep(3)
        # re-find the search bar
        search_bar = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Bạn tìm gì hôm nay"]'))
        )
    # Close the webdriver
    driver.quit()