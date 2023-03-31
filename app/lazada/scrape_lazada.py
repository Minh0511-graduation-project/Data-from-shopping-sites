import json
import time
import os

import pymongo
from selenium import webdriver
from selenium.webdriver import ActionChains
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

    driver = webdriver.Chrome("./chromedriver/chromedriver110/chromedriver", chrome_options=chrome_options)
    driver.maximize_window()
    # Navigate to the Lazada Vietnam website
    driver.get(lazada_url)
    print("scraping lazada")

    # Wait for the search bar to be present and interactable
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="q"]')))
    print("line42:", search_bar)

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
        retry_count = 5
        for i in range(retry_count):
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
                search_bar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="q"]')))
                print("line 84:", search_bar)
                break
            except (NoSuchElementException, StaleElementReferenceException) as e:
                if i == retry_count - 1:
                    raise e
                else:
                    print("Line 90 Retrying...")
                    continue

    with open("app/lazada/lazada_search_suggestions.json", "w") as file:
        json.dump(suggestion_results, file, default=serialize_suggestion, indent=4, ensure_ascii=False)

    with open("app/lazada/lazada_products.json", "w") as file:
        json.dump(product_results, file, default=serialize_product, indent=4, ensure_ascii=False)

    # Close the webdriver
    print("Finished scraping lazada")
    driver.quit()


def scrape_products(search_bar, suggestion_to_db, product_results, products, driver, site):
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
    for suggestion in suggestion_to_db["suggestions"]:
        retry_count = 5
        for i in range(retry_count):
            try:
                print("line 110:", suggestion, search_bar)
                search_bar.send_keys(Keys.CONTROL + "a")
                search_bar.send_keys(Keys.DELETE)
                search_bar.send_keys(suggestion)
                search_bar.send_keys(Keys.ENTER)
                driver.implicitly_wait(20)
                product_list = driver.find_element(By.XPATH, '//div[@class="_17mcb"]')
                print("line 116:", product_list)

                # map the product name with the product price, as a dictionary
                search_term_product_name = {}
                search_term_product_name_price = {}
                search_term_product_name_image = {}
                search_term_product_name_updated_at = {}
                search_term_product_name_url = {}
                i = 0
                for product in product_list.find_elements(By.CLASS_NAME, 'qmXQo'):
                    if i == 5:
                        break
                    try_count = 5
                    for index in range(try_count):
                        try:
                            product_name = product.find_element(By.CLASS_NAME, 'RfADt').text
                            print("132",product_name)
                            product_price = product.find_element(By.CLASS_NAME, 'aBrP0').text
                            print("134",product_price)
                            product_image = product.find_element(By.CSS_SELECTOR,
                                                                 "img.jBwCF").get_attribute('src')
                            print("137",product_image)
                            product_url = product.find_element(By.XPATH, '//div[@class="_95X4G"]/a').get_attribute(
                                'href')
                            print("140",product_url)
                            search_term_product_name[suggestion] = product_name
                            search_term_product_name_price[product_name] = product_price
                            search_term_product_name_image[product_name] = product_image
                            search_term_product_name_updated_at[product_name] = time.time()
                            search_term_product_name_url[product_name] = product_url
                            product_result = ProductDetails(site, suggestion, search_term_product_name[suggestion],
                                                            search_term_product_name_price[product_name],
                                                            search_term_product_name_image[product_name],
                                                            search_term_product_name_updated_at[product_name],
                                                            search_term_product_name_url[product_name])
                            product_to_db = serialize_product(product_result)
                            filter = {
                                "name": product_to_db["name"],
                                "productUrl": product_to_db["productUrl"]
                            }

                            update = {
                                "$set": product_to_db
                            }

                            products.update_one(
                                filter,
                                update,
                                upsert=True
                            )
                            product_results.append(product_result)
                            break
                        except (NoSuchElementException, StaleElementReferenceException) as e:
                            if index == try_count - 1:
                                raise e
                            else:
                                print("Line 172 Retrying...")
                                continue
                    i += 1

                # re-find the search bar
                search_bar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@id="q"]')))
                print("179",search_bar)
                break
            except (NoSuchElementException, StaleElementReferenceException) as e:
                if i == retry_count - 1:
                    raise e
                else:
                    print("line 185 Retrying...")
                    continue
