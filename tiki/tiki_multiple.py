import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

# Initialize the webdriver
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
# Navigate to the Tiki Vietnam website
driver.get("https://tiki.vn/")

# Wait for the search bar to be present and interactable
search_bar = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Bạn tìm gì hôm nay"]'))
)


class Result:
    def __init__(self, keyword, suggestions):
        self.keyword = keyword
        self.suggestions = suggestions


results = []

with open('../search_terms.txt', 'r') as f:
    search_terms = f.read().splitlines()


for search_term in search_terms:
    search_bar.send_keys(Keys.CONTROL + "a")
    search_bar.send_keys(Keys.DELETE)
    search_bar.send_keys(search_term)
    time.sleep(2)
    suggestion_list = driver.find_element(By.XPATH,
                                          '//div[@class="style__StyledSuggestion-sc-1y3xjh6-0 gyELMq revamp"]')
    suggestion_keywords = [item.text for item in suggestion_list.find_elements(By.CLASS_NAME, 'keyword')]
    result = Result(search_term, suggestion_keywords)
    results.append(result)


def serialize_result(obj):
    if isinstance(obj, Result):
        return {"keyword": obj.keyword, "suggestions": obj.suggestions}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")


with open("tiki.json", "w") as file:
    json.dump(results, file, default=serialize_result, indent=4)

# Close the webdriver
driver.quit()
