import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def scrape_lazada_single(lazada_url):
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the Lazada Vietnam website
    driver.get(lazada_url)

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="q"]'))
    )

    search_term = "lazada"

    # Enter a search term
    search_bar.send_keys(search_term)
    time.sleep(5)

    suggestion_list = driver.find_element(By.CLASS_NAME, 'suggest-list--3Tm8')

    suggestion_keywords = [item.text for item in suggestion_list.find_elements(By.CLASS_NAME, 'suggest-common--2KmE ')]

    with open("app/lazada/lazada_search_suggestions.json", "w") as file:
        file.write(
            json.dumps({"search_term": search_term, "suggestions": suggestion_keywords}, indent=4, ensure_ascii=False))

    # Close the webdriver
    driver.quit()
