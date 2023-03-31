import json
import os
import time

import pymongo
import requests
from dotenv import load_dotenv

from model.auto_suggestions_results import Result, serialize_suggestion
from model.product_details import ProductDetails, serialize_product


def get_tiki_from_API(directory, db_url):
    print("get tiki from API")
    load_dotenv()
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    search_suggestions = db['tiki search suggestions']
    products = db['tiki products']
    tiki_search_suggestion_url = os.getenv('TIKI_SEARCH_SUGGESTION_URL')
    tiki_search_product_url = os.getenv('TIKI_TOP_SELL_PRODUCTS_URL')
    tiki_url = "https://tiki.vn/"

    search_terms = []

    site = "tiki"

    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            with open(os.path.join(directory, file_name), 'r') as file:
                lines = file.read().splitlines()
                for line in lines:
                    search_terms.append(line.split(',')[0])

    headers = {
        "User-Agent": os.getenv('USER_AGENT')
    }

    for search_term in search_terms:
        params = {
            'trackity_id': '8bca1f0a-60c6-b0c6-b572-aa31021a2396',
            'q': search_term,
        }

        response = requests.get(tiki_search_suggestion_url, params=params, headers=headers)

        if response.status_code == 200:
            print(response.url)
            response_data = response.json()
            # if there is no data field in the response, then skip this search term
            if 'data' not in response_data:
                continue
            suggestion_data = response_data['data']
            suggestion_keywords = []
            suggestion_results = []
            suggestion_keywords_results = []
            for data in suggestion_data:
                suggestion_updated_at = time.time()
                suggestion_keywords.append(data['keyword'])
                suggestion_result = Result(site, search_term, suggestion_keywords, suggestion_updated_at)
                suggestion_to_db = serialize_suggestion(suggestion_result)
                search_suggestions.update_one(
                    {"keyword": suggestion_to_db["keyword"]},
                    {"$set": suggestion_to_db},
                    upsert=True
                )
                suggestion_keywords_results = suggestion_to_db["suggestions"]
                suggestion_results.append(suggestion_result)

                with open("app/tiki/tiki_search_suggestions.json", "w") as file:
                    json.dump(suggestion_results, file, default=serialize_suggestion, indent=4, ensure_ascii=False)

            scrape_shopee_products(suggestion_keywords_results, tiki_search_product_url, tiki_url, headers, products, site)


def scrape_shopee_products(suggestion_keywords_results, tiki_search_product_url, tiki_url, headers, products, site):
    product_results = []
    for suggestion in suggestion_keywords_results:
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
            print(response.url)
            product_data = response.json()
            if 'data' not in product_data:
                continue
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
                i += 1

            with open("app/tiki/tiki_products.json", "w") as file:
                json.dump(product_results, file, default=serialize_product, indent=4, ensure_ascii=False)
