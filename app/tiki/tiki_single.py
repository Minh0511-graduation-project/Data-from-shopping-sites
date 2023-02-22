import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def scrape_tiki_single(tiki_url):
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the Tiki Vietnam website
    driver.get(tiki_url)

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Bạn tìm gì hôm nay"]'))
    )

    search_term = "tiki"

    # Enter a search term
    search_bar.send_keys(search_term)
    time.sleep(5)

    suggestion_list = driver.find_element(By.XPATH,
                                          '//div[@class="style__StyledSuggestion-sc-1y3xjh6-0 gyELMq revamp"]')

    suggestion_keywords = [item.text for item in suggestion_list.find_elements(By.CLASS_NAME, 'keyword')]

    with open("app/tiki/tiki_search_suggestions.json", "w") as file:
        file.write(
            json.dumps({"search_term": search_term, "suggestions": suggestion_keywords}, indent=4, ensure_ascii=False))

    # wait for 5 seconds before close the webdriver
    time.sleep(5)

    # Close the webdriver
    driver.quit()
