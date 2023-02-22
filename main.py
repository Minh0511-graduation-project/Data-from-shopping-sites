import concurrent.futures
import os

from app.lazada.lazada_search_suggestions import scrape_lazada_search_suggestions
from app.shopee.shopee_to_mongodb import shopee_to_mongo
from app.tiki.tiki_search_suggestions import scrape_tiki_search_suggestions
from app.shopee.shopee_search_suggestions import scrape_shopee_search_suggestions
from app.tiki.tiki_products import scrape_tiki_products
from app.tiki.tiki_to_mongodb import tiki_to_mongo
from app.shopee.shopee_products import scrape_shopee_products


def scrape_search_suggestions(directory):
    args_search_suggestions = [(scrape_shopee_search_suggestions, ('https://shopee.vn/', directory)),
                               (scrape_tiki_search_suggestions, ('https://tiki.vn/', directory))]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, *args_tuple) for f, args_tuple in args_search_suggestions]

        # Wait for all futures to complete
        results_search_suggestions = [future.result() for future in
                                      concurrent.futures.as_completed(futures)]


def scrape_products():
    args_products = [(scrape_shopee_products, 'https://shopee.vn/'),
                     (scrape_tiki_products, 'https://tiki.vn/')]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, args) for f, args in args_products]

        # Wait for all futures to complete
        results_products = [future.result() for future in concurrent.futures.as_completed(futures)]


def push_to_db(db_url):
    args_products = [(tiki_to_mongo, db_url),
                     (shopee_to_mongo, db_url)]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, args) for f, args in args_products]

        # Wait for all futures to complete
        results = [future.result() for future in concurrent.futures.as_completed(futures)]


if __name__ == '__main__':
    db_url = os.environ.get('MONGO_URL')
    directory = 'vi-wordnet'
    scrape_search_suggestions(directory)
    scrape_products()
    push_to_db(db_url)
