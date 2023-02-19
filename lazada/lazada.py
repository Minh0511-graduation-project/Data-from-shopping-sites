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
# Navigate to the Lazada Vietnam website
driver.get("https://www.lazada.vn/")

# Wait for the search bar to be present and interactable
search_bar = WebDriverWait(driver, 1).until(
    EC.element_to_be_clickable((By.XPATH, '//input[@id="q"]'))
)
end = time.time()
print("Lazada Elapsed time since start until perform automation: ", end - start, "seconds")

search_term = "lazada"

# Enter a search term
search_bar.send_keys(search_term)
time.sleep(5)

suggestion_list = driver.find_element(By.CLASS_NAME, 'suggest-list--3Tm8')

suggestion_keywords = [item.text for item in suggestion_list.find_elements(By.CLASS_NAME, 'suggest-common--2KmE ')]

with open("lazada.json", "w") as file:
    file.write(json.dumps({"search_term": search_term, "suggestions": suggestion_keywords}, indent=4))

# Close the webdriver
driver.quit()
