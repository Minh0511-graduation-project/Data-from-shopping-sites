import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from model.product_details import ProductDetails, serialize_result


def scrape_lazada_products(lazada_url):
    # Initialize the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    # Navigate to the lazada Vietnam website
    driver.get(lazada_url)

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@id="q"]'))
    )

    with open('app/lazada/lazada_search_suggestions.json') as f:
        data = json.load(f)

    # get all the suggestions and store it in an array
    search_suggestions = []
    for _, e in enumerate(data):
        search_suggestions.append(e['suggestions'])

    # flatten the array
    search_suggestions = [item for sublist in search_suggestions for item in sublist]
    results = []

    site = 'lazada'
    for suggestion in search_suggestions:
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(suggestion)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(5)

        product_list = driver.find_element(By.XPATH, '//div[@class="_17mcb"]')
        # map the product name with the product price, as a dictionary
        search_term_product_name = {}
        search_term_product_name_price = {}
        search_term_product_name_image = {}
        i = 0
        for product in product_list.find_elements(By.CLASS_NAME, 'qmXQo'):
            if i == 5:
                break
            product_name = product.find_element(By.CLASS_NAME, 'RfADt').text
            product_price = product.find_element(By.CLASS_NAME, 'aBrP0').text
            product_image = product.find_element(By.CSS_SELECTOR,
                                                 "img.jBwCF").get_attribute('src')
            search_term_product_name[suggestion] = product_name
            search_term_product_name_price[product_name] = product_price
            search_term_product_name_image[product_name] = product_image
            result = ProductDetails(site, suggestion, search_term_product_name[suggestion],
                                    search_term_product_name_price[product_name],
                                    search_term_product_name_image[product_name])
            results.append(result)
            i += 1

        # re-find the search bar
        search_bar = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="q"]'))
        )

    with open("app/lazada/lazada_products.json", "w") as file:
        json.dump(results, file, default=serialize_result, indent=4, ensure_ascii=False)
    # Close the webdriver
    driver.quit()

