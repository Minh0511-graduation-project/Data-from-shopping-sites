import json
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from model.auto_suggestions_results import Result, serialize_result


def scrape_shopee_search_suggestions(shopee_url, directory):
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the shopee Vietnam website
    driver.get(shopee_url)

    # close popup
    close_btn = driver.execute_script(
        'return document.querySelector("#main shopee-banner-popup-stateful").shadowRoot.querySelector("div.home-popup__close-area div.shopee-popup__close-btn")')
    close_btn.click()
    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'shopee-searchbar-input__input'))
    )

    results = []

    search_terms = []

    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            with open(os.path.join(directory, file_name), 'r') as file:
                lines = file.read().splitlines()
                for line in lines:
                    search_terms.append(line.split(',')[0])

    for search_term in search_terms:
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(search_term)
        time.sleep(1)
        suggestion_list = driver.find_element(By.XPATH,
                                              '//div[@id="shopee-searchbar-listbox"]')
        suggestion_keywords = [item.text for item in suggestion_list.find_elements(
            By.CLASS_NAME, 'shopee-searchbar-hints__entry__product-name')]
        result = Result(search_term, suggestion_keywords)
        results.append(result)

    with open("app/shopee/shopee_search_suggestions.json", "w") as file:
        json.dump(results, file, default=serialize_result, indent=4, ensure_ascii=False)

    # Close the webdriver
    driver.quit()
