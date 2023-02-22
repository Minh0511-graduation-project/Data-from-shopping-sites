import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from model.product_details import ProductDetails, serialize_result


def scrape_shopee_products(shopee_url):
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the Tiki Vietnam website
    driver.get(shopee_url)

    # close popup
    close_btn = driver.execute_script(
        'return document.querySelector("#main shopee-banner-popup-stateful").shadowRoot.querySelector("div.home-popup__close-area div.shopee-popup__close-btn")')
    close_btn.click()

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'shopee-searchbar-input__input'))
    )

    with open('app/shopee/shopee_search_suggestions.json') as f:
        data = json.load(f)

    # get all the suggestions and store it in an array
    search_suggestions = []
    for _, e in enumerate(data):
        search_suggestions.append(e['suggestions'])

    # flatten the array
    search_suggestions = [item for sublist in search_suggestions for item in sublist]
    results = []

    for suggestion in search_suggestions:
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(suggestion)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(5)
        best_seller = driver.find_element(By.XPATH, '//div[@class="shopee-sort-bar"]//div[3]')
        best_seller.click()
        time.sleep(5)

        product_list = driver.find_element(By.XPATH, '//div[@class="row shopee-search-item-result__items"]')
        # map the product name with the product price, as a dictionary
        product_name_price = {}
        i = 0
        for product in product_list.find_elements(By.CLASS_NAME, 'KMyn8J'):
            if i == 5:
                break
            product_name = product.find_element(By.CLASS_NAME, 'Cve6sh').text
            product_price = product.find_element(By.CLASS_NAME, 'hpDKMN').text
            product_name_price[product_name] = product_price
            result = ProductDetails(product_name, product_name_price[product_name])
            results.append(result)
            i += 1

        # re-find the search bar
        search_bar = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'shopee-searchbar-input__input'))
        )

    with open("app/shopee/shopee_products.json", "w") as file:
        json.dump(results, file, default=serialize_result, indent=4, ensure_ascii=False)
    # Close the webdriver
    driver.quit()

