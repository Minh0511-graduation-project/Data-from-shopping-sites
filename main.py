import concurrent.futures
import os
import time

from app.lazada.lazada_search_suggestions import scrape_lazada_search_suggestions
from app.tiki.tiki_search_suggestions import scrape_tiki_search_suggestions
from app.shopee.shopee_search_suggestions import scrape_shopee_search_suggestions
from app.tiki.tiki_products import scrape_tiki_products
from app.shopee.shopee_products import scrape_shopee_products
from app.lazada.lazada_products import scrape_lazada_products


def scrape_search_suggestions(directory, db_url):
    args_search_suggestions = [(scrape_lazada_search_suggestions, ('https://www.lazada.vn/', directory, db_url)),
                               (scrape_shopee_search_suggestions, ('https://shopee.vn/', directory, db_url)),
                               (scrape_tiki_search_suggestions, ('https://tiki.vn/', directory, db_url))]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, *args_tuple) for f, args_tuple in args_search_suggestions]

        # Wait for all futures to complete
        results_search_suggestions = [future.result() for future in
                                      concurrent.futures.as_completed(futures)]


def scrape_products(db_url):
    args_products = [(scrape_lazada_products, ('https://www.lazada.vn/', db_url)),
                     (scrape_shopee_products, ('https://shopee.vn/', db_url)),
                     (scrape_tiki_products, ('https://tiki.vn/', db_url))]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, *args_tuple) for f, args_tuple in args_products]

        # Wait for all futures to complete
        results_products = [future.result() for future in concurrent.futures.as_completed(futures)]


if __name__ == '__main__':
    while True:
        db_url = os.environ.get('MONGO_URL')
        directory = 'vi-wordnet'
        mockDir = 'mock'
        scrape_search_suggestions(mockDir, db_url)
        scrape_products(db_url)
        # sleep for 3 hour
        time.sleep(10800)
