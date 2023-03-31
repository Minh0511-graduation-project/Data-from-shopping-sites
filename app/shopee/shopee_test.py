import json
import time
import os

import pymongo
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from model.auto_suggestions_results import Result, serialize_suggestion
from model.product_details import ProductDetails, serialize_product


def scrape_shopee_test(shopee_url):
    # Initialize the webdriver
    # chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("./chromedriver/chromedriver110/chromedriver")
    driver.maximize_window()
    # Navigate to the shopee Vietnam website
    driver.get(shopee_url)
    actions = ActionChains(driver)

    driver.implicitly_wait(20)

    user_name = driver.find_element(By.XPATH, '//input[@placeholder="Email/Số điện thoại/Tên đăng nhập"]')
    password = driver.find_element(By.XPATH, '//input[@placeholder="Mật khẩu"]')

    user_name.send_keys("0856147365")
    password.send_keys("Minh0511")
    password.send_keys(Keys.ENTER)

    driver.implicitly_wait(20)
    close_modal_btn = driver.find_element(By.XPATH, '//div[@class="shopee-modal guide-modal"]//button[@type="button"]')
    close_modal_btn.click()

    tip_content_btn = driver.find_element(By.XPATH, '//div[@class="tip-content"]//button[@type="button"]')
    tip_content_btn.click()

    driver.implicitly_wait(20)
    add_item = driver.find_element(By.XPATH, '//span[@class="add-btn"]')
    add_item.click()

    driver.implicitly_wait(20)
    check_box = driver.find_element(By.XPATH, '//td[@class="is-first"]//span[@class="shopee-checkbox__indicator"]')
    check_box.click()

    driver.implicitly_wait(20)
    confirm_add = driver.find_element(By.XPATH, '//div[@class="shopee-modal__footer with-assist"]//button[2]')
    confirm_add.click()

    element = driver.find_element(By.XPATH, '//div[@class="right"]//div[@class="shopee-form-item__control"]')
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="right"]//div[@class="shopee-form-item__control"]')))
    actions.click(element).perform()

    driver.implicitly_wait(20)
    confirm_btn = driver.find_element(By.XPATH,
                                      '//div[@x-placement="top"]//div[@class="shopee-popover__content"]//div//div//button[@type="button"]')
    confirm_btn.click()

    driver.implicitly_wait(20)
    add_more_keyword = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="keywords-controls"]//button[1]')))
    add_more_keyword.click()

    driver.implicitly_wait(20)
    input_search_key = driver.find_element(By.XPATH, '//input[@placeholder="Nhập từ khóa của bạn tại đây"]')
    input_search_key.send_keys("iphone mini")
    input_search_key.send_keys(Keys.ENTER)

    time.sleep(5)
    suggestion_list = driver.find_element(By.XPATH,
                                          '//div[@class="shopee-table"]//table[@class="shopee-table__body"]//tbody')
    time.sleep(5)
    suggestion_counter = [item for item in suggestion_list.find_elements(
        By.CLASS_NAME, 'shopee-table__cell')]
    time.sleep(5)
    suggestion_keyword = [item for item in suggestion_list.find_elements(
        By.CLASS_NAME, 'keyword')]

    result = []
    suggestion_counter_result = []
    for keyword in suggestion_keyword:
        result.append(keyword.text)

    print(result)

    for counter in suggestion_counter:
        suggestion_counter_result.append(counter.text)

    new_result = []
    sub_result = []
    for i in range(len(suggestion_counter_result)):
        sub_result.append(suggestion_counter_result[i])
        if (i + 1) % 5 == 0:
            new_result.append(sub_result)
            sub_result = []

    print(new_result)

    with open("app/shopee/data.json", "w") as outfile:
        json.dump(new_result, outfile, indent=4, ensure_ascii=False)
    print("scraping shopee")

    # Close the webdriver
    print("scraping shopee done")
    driver.quit()
