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
# Navigate to the shopee Vietnam website
driver.get("https://shopee.vn/")

# close popup
close_btn = driver.execute_script(
    'return document.querySelector("#main shopee-banner-popup-stateful").shadowRoot.querySelector("div.home-popup__close-area div.shopee-popup__close-btn")')
close_btn.click()
# Wait for the search bar to be present and interactable
search_bar = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CLASS_NAME, 'shopee-searchbar-input__input'))
)

end = time.time()
print("Shopee Elapsed time since start until perform automation: ", end - start, "seconds")
search_term = "shopee"

# Enter a search term
search_bar.send_keys(search_term)
time.sleep(5)

suggestion_list = driver.find_element(By.XPATH, '//div[@id="shopee-searchbar-listbox"]')

suggestion_keywords = [item.text for item in
                       suggestion_list.find_elements(By.CLASS_NAME, 'shopee-searchbar-hints__entry__product-name')]

with open("shopee.json", "w") as file:
    file.write(json.dumps({"search_term": search_term, "suggestions": suggestion_keywords}, indent=4))

# wait for 5 seconds before close the webdriver
time.sleep(5)

# Close the webdriver
driver.quit()
