import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# set headless, this will disable browser's UI
# comment this and remove options in driver if you want to see how automation works
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

start = time.time()

# Initialize the webdriver
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.maximize_window()
# Navigate to the Tiki Vietnam website
driver.get("https://tiki.vn/")

# Wait for the search bar to be present and interactable
search_bar = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Bạn tìm gì hôm nay"]'))
)

search_term = "tiki"

end = time.time()
print("Tiki Elapsed time since start until perform automation: ", end - start, "seconds")

# Enter a search term
search_bar.send_keys(search_term)
time.sleep(5)

suggestion_list = driver.find_element(By.XPATH, '//div[@class="style__StyledSuggestion-sc-1y3xjh6-0 gyELMq revamp"]')

suggestion_keywords = [item.text for item in suggestion_list.find_elements(By.CLASS_NAME, 'keyword')]

with open("tiki.json", "w") as file:
    file.write(json.dumps({"search_term": search_term, "suggestions": suggestion_keywords}, indent=4))

# wait for 5 seconds before close the webdriver
time.sleep(5)

# Close the webdriver
driver.quit()
