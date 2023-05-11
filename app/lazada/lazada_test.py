import json
import time
import os

import pymongo
import requests
from dotenv import load_dotenv
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


def get_Lazada_from_API():
    load_dotenv()
    lazada_url = os.getenv('LAZADA_PRODUCT_API')
    params = {
        "_keyori": "ss",
        "ajax": True,
        "from": "input",
        "isFirstRequest": True,
        "page": 1,
        "q": "c%E1%BB%91c",
        "spm": "a2o4n.searchlist.search.go.2dc96487ecejdh",
    }

    headers = {
        "User-Agent": os.getenv('USER_AGENT')
    }

    response = requests.get(lazada_url, params=params, headers=headers)
    data = response.json()
    print(data)
