import concurrent.futures
import functools
import json
import time
import os

import pymongo
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from model.auto_suggestions_results import Result, serialize_suggestion
from model.keyword_count import KeywordCount, serialize_keyword_count
from model.product_details import ProductDetails, serialize_product


def scrape_shopee_2(shopee_url, directory, db_url):
    load_dotenv()
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    search_suggestions = db['shopee search suggestions']
    products = db['shopee products']
    keyword_count = db['search keyword count']
    shopee_search_suggestion_url = os.getenv('SHOPEE_SEARCH_SUGGESTION_URL')
    shopee_ad_url = os.getenv('SHOPEE_AD_URL')
    # Initialize the webdriver
    # chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("./chromedriver/chromedriver112/chromedriver")
    driver.maximize_window()

    seller_driver = webdriver.Chrome("./chromedriver/chromedriver112/chromedriver")
    seller_driver.maximize_window()
    # Navigate to the shopee Vietnam website
    driver.get(shopee_url)
    seller_driver.get(shopee_ad_url)
    print("scraping shopee")

    # close popup
    driver.implicitly_wait(5)
    close_btn = driver.execute_script(
        'return document.querySelector("#main shopee-banner-popup-stateful").shadowRoot.querySelector("div.home-popup__close-area div.shopee-popup__close-btn")')
    close_btn.click()
    # Wait for the search bar to be present and interactable
    search_bar = driver.find_element(By.CLASS_NAME, 'shopee-searchbar-input__input')

    suggestion_results = []
    product_results = []
    search_terms = []

    site = "shopee"

    already_log_in = False

    suggestion_keywords_results = ["quạt cầm tay", "áo đá bóng"]


    #scrape_products(search_bar, suggestion_keywords_results, product_results, products, driver, site)
    scrape_keyword_count(seller_driver, suggestion_keywords_results, site, keyword_count, already_log_in)
    already_log_in = True

    # Close the webdriver
    print("scraping shopee done")
    driver.quit()


def scrape_products(search_bar, suggestion_keywords_results, product_results, products, driver, site):
    for suggestion in suggestion_keywords_results:
        try:
            search_bar = driver.find_element(By.CLASS_NAME, 'shopee-searchbar-input__input')
            print("scraping products for " + suggestion)
            retry_count = 3
            while retry_count >= 0:
                try:
                    retry_count -= 1
                    search_bar.send_keys(Keys.CONTROL + "a")
                    search_bar.send_keys(Keys.DELETE)
                    search_bar.send_keys(suggestion)
                    search_bar.send_keys(Keys.ENTER)
                    time.sleep(10)
                    best_seller = driver.find_element(By.XPATH, '//div[@class="shopee-sort-bar"]//div[3]')
                    if best_seller is None:
                        continue
                    best_seller.click()
                    time.sleep(10)

                    product_list = driver.find_element(By.XPATH, '//div[@class="row shopee-search-item-result__items"]')
                    if product_list is None:
                        continue
                    # map the product name with the product price, as a dictionary
                    search_term_product_name = {}
                    search_term_product_name_price = {}
                    search_term_product_name_image = {}
                    search_term_product_name_updated_at = {}
                    search_term_product_name_url = {}
                    i = 0
                    for product in product_list.find_elements(By.XPATH,
                                                              '//div[@class="col-xs-2-4 shopee-search-item-result__item"]/a'):
                        if i == 5:
                            break
                        try_count = 3
                        while try_count >= 0:
                            try:
                                try_count -= 1
                                product_name = product.find_element(By.CLASS_NAME, 'Cve6sh').text
                                product_price = product.find_element(By.CLASS_NAME, 'hpDKMN').text
                                product_image = product.find_element(By.CSS_SELECTOR,
                                                                     "img._7DTxhh").get_attribute('src')
                                product_url = product.get_attribute('href')
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
                                    "searchTerm": suggestion,
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
                                continue
                        i += 1

                    # re-find the search bar
                    search_bar = driver.find_element(By.CLASS_NAME, 'shopee-searchbar-input__input')
                    break
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    continue
        except (NoSuchElementException, StaleElementReferenceException) as e:
            driver.implicitly_wait(20)

            user_name = driver.find_element(By.XPATH,
                                                   '//input[@placeholder="Email/Số điện thoại/Tên đăng nhập"]')
            password = driver.find_element(By.XPATH, '//input[@placeholder="Mật khẩu"]')

            user_name.send_keys(os.getenv('SHOPEE_SELLER_USERNAME'))
            password.send_keys(os.getenv('SHOPEE_SELLER_PASSWORD'))
            password.send_keys(Keys.ENTER)
            continue


def scrape_keyword_count(seller_driver, suggestion_keywords_results, site, keyword_count, already_log_in):
    print(already_log_in)
    actions = ActionChains(seller_driver)

    if not already_log_in:
        seller_driver.implicitly_wait(20)

        user_name = seller_driver.find_element(By.XPATH, '//input[@placeholder="Email/Số điện thoại/Tên đăng nhập"]')
        password = seller_driver.find_element(By.XPATH, '//input[@placeholder="Mật khẩu"]')

        user_name.send_keys(os.getenv('SHOPEE_SELLER_USERNAME'))
        password.send_keys(os.getenv('SHOPEE_SELLER_PASSWORD'))
        password.send_keys(Keys.ENTER)

        seller_driver.implicitly_wait(20)
        close_modal_btn = seller_driver.find_element(By.XPATH,
                                                     '//div[@class="shopee-modal guide-modal"]//button[@type="button"]')
        close_modal_btn.click()

        tip_content_btn = seller_driver.find_element(By.XPATH, '//div[@class="tip-content"]//button[@type="button"]')
        tip_content_btn.click()

        seller_driver.implicitly_wait(20)
        add_item = seller_driver.find_element(By.XPATH, '//span[@class="add-btn"]')
        add_item.click()

        seller_driver.implicitly_wait(20)
        check_box = seller_driver.find_element(By.XPATH,
                                               '//td[@class="is-first"]//span[@class="shopee-checkbox__indicator"]')
        check_box.click()

        seller_driver.implicitly_wait(20)
        confirm_add = seller_driver.find_element(By.XPATH, '//div[@class="shopee-modal__footer with-assist"]//button[2]')
        confirm_add.click()

        element = seller_driver.find_element(By.XPATH, '//div[@class="right"]//div[@class="shopee-form-item__control"]')
        actions = ActionChains(seller_driver)
        actions.move_to_element(element).perform()
        wait = WebDriverWait(seller_driver, 10)
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="right"]//div[@class="shopee-form-item__control"]')))
        actions.click(element).perform()

        seller_driver.implicitly_wait(20)
        confirm_btn = seller_driver.find_element(By.XPATH,
                                                 '//div[@x-placement="top"]//div[@class="shopee-popover__content"]//div//div//button[@type="button"]')
        confirm_btn.click()

        seller_driver.implicitly_wait(20)
        add_more_keyword = WebDriverWait(seller_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="keywords-controls"]//button[1]')))
        add_more_keyword.click()

    seller_driver.implicitly_wait(20)
    input_search_key = seller_driver.find_element(By.XPATH, '//input[@placeholder="Nhập từ khóa của bạn tại đây"]')
    for suggestion in suggestion_keywords_results:
        print(suggestion)
        try_count = 3
        while try_count >= 0:
            try:
                try_count -= 1
                input_search_key.send_keys(Keys.CONTROL + "a")
                input_search_key.send_keys(Keys.DELETE)
                input_search_key.send_keys(suggestion)
                input_search_key.send_keys(Keys.ENTER)

                time.sleep(5)
                suggestion_list = seller_driver.find_element(By.XPATH,
                                                             '//div[@class="shopee-table"]//table[@class="shopee-table__body"]//tbody')
                time.sleep(5)
                suggestion_counter = [item for item in suggestion_list.find_elements(
                    By.CLASS_NAME, 'shopee-table__cell')]

                suggestion_counter_result = []

                for counter in suggestion_counter:
                    suggestion_counter_result.append(counter.text)

                trimmed_result = []
                sub_result = []
                for i in range(len(suggestion_counter_result)):
                    sub_result.append(suggestion_counter_result[i])
                    if (i + 1) % 5 == 0:
                        trimmed_result.append(sub_result)
                        sub_result = []

                data_filtered = []
                for sublist in trimmed_result:
                    if sublist != ['', '', '', '', '']:
                        if 'Hot' in sublist[0]:
                            sublist[0] = sublist[0].replace(' Hot', '')
                        data_filtered.append([sublist[0], sublist[2]])

                count_result = []
                updated_at = time.time()
                for sublist in data_filtered:
                    count = int(sublist[1].replace(".", ""))
                    obj = KeywordCount(site, suggestion, count, updated_at)
                    count_to_db = serialize_keyword_count(obj)
                    count_result.append(count_to_db)

                filter = {
                    "site": site,
                    "keyword": suggestion
                }

                update = {
                    "$set": count_result[0]
                }

                keyword_count.update_one(
                    filter,
                    update,
                    upsert=True
                )
                break
            except (NoSuchElementException, StaleElementReferenceException) as e:
                continue

