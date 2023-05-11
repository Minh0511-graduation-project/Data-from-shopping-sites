import concurrent.futures
import functools
import json
import os
import time

import pymongo
import requests
from dotenv import load_dotenv

from model.auto_suggestions_results import Result, serialize_suggestion
from model.keyword_count import serialize_keyword_count, KeywordCount
from model.product_details import ProductDetails, serialize_product


def get_tiki_from_API_2(db_url):
    print("get tiki from API")
    load_dotenv()
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    search_suggestions = db['tiki search suggestions']
    products = db['tiki products']
    keyword_count = db['search keyword count']
    tiki_search_suggestion_url = os.getenv('TIKI_SEARCH_SUGGESTION_URL')
    tiki_search_product_url = os.getenv('TIKI_TOP_SELL_PRODUCTS_URL')
    tiki_keyword_stat_url = os.getenv('TIKI_KEYWORD_STAT_URL')
    tiki_url = "https://tiki.vn/"

    search_terms = []
    suggestion_results = []
    product_results = []

    site = "tiki"
    headers = {
        "User-Agent": os.getenv('USER_AGENT')
    }

    suggestion = "áo thun polo nam"

    scrape_keyword_count(suggestion, headers, tiki_keyword_stat_url, site, keyword_count)
    scrape_tiki_products(suggestion, tiki_search_product_url, headers, tiki_url, site, products,
                         product_results)

    print("get tiki from API done")


def scrape_keyword_count(suggestion, headers, tiki_keyword_stat_url, site, keyword_count):
    body = {
        "payment_model": "CPC",
        "excluded_business": 157998,
        "keywords": [
            suggestion
        ],
        "product_id": [
            249220939
        ],
    }
    json_body = json.dumps(body)
    response = requests.post(tiki_keyword_stat_url, data=json_body, headers=headers)

    if response.status_code == 200:
        keyword_count_data = response.json()
        keyword_count_updated_at = time.time()
        count = keyword_count_data['data']['keywords'][0]['total_search_volume']
        keyword_count_result = KeywordCount(site, suggestion, count, keyword_count_updated_at)
        keyword_count_to_db = serialize_keyword_count(keyword_count_result)
        filter = {
            "site": site,
            "keyword": keyword_count_to_db["keyword"]
        }

        update = {
            "$set": keyword_count_to_db
        }

        keyword_count.update_one(
            filter,
            update,
            upsert=True
        )


def scrape_tiki_products(suggestion, tiki_search_product_url, headers, tiki_url, site, products,
                         product_results):
    # map the product name with the product price, as a dictionary
    search_term_product_name = {}
    search_term_product_name_price = {}
    search_term_product_name_image = {}
    search_term_product_name_updated_at = {}
    search_term_product_name_url = {}

    params = {
        'limit': 40,
        'include': "advertisement",
        'trackity_id': 'dfddd561-8193-a305-1e29-fcc64ee96202',
        'q': suggestion,
        'sort': 'top_seller'
    }

    response = requests.get(tiki_search_product_url, params=params, headers=headers)
    if response.status_code == 200:
        product_data = response.json()
        i = 0
        for data in product_data['data']:
            if i == 5:
                break
            product_updated_at = time.time()
            product_name = data['name']
            search_term_product_name[suggestion] = product_name
            search_term_product_name_price[product_name] = "₫" + str(data['price'])
            search_term_product_name_image[product_name] = data['thumbnail_url']
            search_term_product_name_updated_at[product_name] = product_updated_at
            search_term_product_name_url[product_name] = tiki_url + data['url_path']

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
            product_results.append(product_to_db)
            i += 1
