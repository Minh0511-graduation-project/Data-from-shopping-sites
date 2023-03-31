import concurrent.futures
import os
import time
from dotenv import load_dotenv

from app.lazada.scrape_lazada import scrape_lazada
from app.shopee.shopee_test import scrape_shopee_test
from app.tiki.consume_tiki_from_API import get_tiki_from_API
from app.tiki.scrape_tiki import scrape_tiki
from app.shopee.scrape_shopee import scrape_shopee


def scrape_shopping_sites(directory, db_url):
    args_search_suggestions = [(scrape_lazada, ('https://www.lazada.vn/', directory, db_url)),
                               (scrape_lazada, ('https://www.lazada.vn/', directory, db_url)),
                                (scrape_lazada, ('https://www.lazada.vn/', directory, db_url))]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, *args_tuple) for f, args_tuple in args_search_suggestions]

        # Wait for all futures to complete
        results_search_suggestions = [future.result() for future in
                                      concurrent.futures.as_completed(futures)]


if __name__ == '__main__':
    load_dotenv()
    directory = 'vi-wordnet'
    mockDir = 'mock'
    db_url = os.getenv('MONGO_URL')
    scrape_shopee('https://shopee.vn/', mockDir, db_url)
