import json
import time
import os

import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from model.auto_suggestions_results import Result, serialize_suggestion
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from model.product_details import ProductDetails, serialize_product


def scrape_lazada(lazada_url, directory, db_url):
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    search_suggestions = db['lazada search suggestions']
    products = db['lazada products']
    # Initialize the webdriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("./chromedriver/chromedriver110/chromedriver", options=chrome_options)
    driver.maximize_window()
    # Navigate to the Lazada Vietnam website
    driver.get(lazada_url)
    print("scraping lazada")

    # Wait for the search bar to be present and interactable
    search_bar = driver.find_element(By.XPATH, '//input[@id="q"]')

    suggestion_results = []
    product_results = []

    search_terms = []

    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            with open(os.path.join(directory, file_name), 'r') as file:
                lines = file.read().splitlines()
                for line in lines:
                    search_terms.append(line.split(',')[0])

    site = "lazada"

    for search_term in search_terms:
        try:
            search_bar.send_keys(Keys.CONTROL + "a")
            search_bar.send_keys(Keys.DELETE)
            search_bar.send_keys(search_term)
            time.sleep(10)
            suggestion_list = driver.find_element(By.CLASS_NAME, 'suggest-list--3Tm8')

            suggestion_keywords = [item.text for item in
                                   suggestion_list.find_elements(By.CLASS_NAME, 'suggest-common--2KmE ')]
            suggestion_updated_at = time.time()
            suggestion_result = Result(site, search_term, suggestion_keywords, suggestion_updated_at)
            suggestion_to_db = serialize_suggestion(suggestion_result)
            search_suggestions.update_one(
                {"keyword": suggestion_to_db["keyword"]},
                {"$set": suggestion_to_db},
                upsert=True
            )
            suggestion_results.append(suggestion_result)
            scrape_products(search_bar, suggestion_to_db, product_results, products, driver, site)

            # re-find the search bar
            search_bar = driver.find_element(By.XPATH, '//input[@id="q"]')
        except NoSuchElementException:
            print("no such element")
            continue
        except StaleElementReferenceException:
            print("stale element reference")
            continue

    with open("app/lazada/lazada_search_suggestions.json", "w") as file:
        json.dump(suggestion_results, file, default=serialize_suggestion, indent=4, ensure_ascii=False)

    with open("app/lazada/lazada_products.json", "w") as file:
        json.dump(product_results, file, default=serialize_product, indent=4, ensure_ascii=False)

    # Close the webdriver
    print("Finished scraping lazada")
    driver.quit()


def scrape_products(search_bar, suggestion_to_db, product_results, products, driver, site):
    try:
        for suggestion in suggestion_to_db["suggestions"]:
            search_bar.send_keys(Keys.CONTROL + "a")
            search_bar.send_keys(Keys.DELETE)
            search_bar.send_keys(suggestion)
            search_bar.send_keys(Keys.ENTER)
            time.sleep(10)
            product_list = driver.find_element(By.XPATH, '//div[@class="_17mcb"]')

            # map the product name with the product price, as a dictionary
            search_term_product_name = {}
            search_term_product_name_price = {}
            search_term_product_name_image = {}
            search_term_product_name_updated_at = {}
            i = 0
            for product in product_list.find_elements(By.CLASS_NAME, 'qmXQo'):
                try:
                    if i == 5:
                        break
                    product_name = product.find_element(By.CLASS_NAME, 'RfADt').text
                    product_price = product.find_element(By.CLASS_NAME, 'aBrP0').text
                    product_image = product.find_element(By.CSS_SELECTOR,
                                                         "img.jBwCF").get_attribute('src')
                    search_term_product_name[suggestion] = product_name
                    search_term_product_name_price[product_name] = product_price
                    search_term_product_name_image[product_name] = product_image
                    search_term_product_name_updated_at[product_name] = time.time()
                    product_result = ProductDetails(site, suggestion, search_term_product_name[suggestion],
                                                    search_term_product_name_price[product_name],
                                                    search_term_product_name_image[product_name],
                                                    search_term_product_name_updated_at[product_name])
                    result_to_db = serialize_product(product_result)
                    products.update_one(
                        {"name": result_to_db["name"]},
                        {"$set": result_to_db},
                        upsert=True
                    )
                    product_results.append(product_result)
                    i += 1
                except NoSuchElementException:
                    print("no such element")
                    continue
                except StaleElementReferenceException:
                    print("stale element reference")
                    continue

            # re-find the search bar
            search_bar = driver.find_element(By.XPATH, '//input[@id="q"]')
    except NoSuchElementException:
        print("no such element")
        pass
    except StaleElementReferenceException:
        print("stale element reference")
        pass
