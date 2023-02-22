import concurrent.futures
import os

from app.lazada.lazada_search_suggestions import scrape_lazada_search_suggestions
from app.tiki.tiki_search_suggestions import scrape_tiki_search_suggestions
from app.shopee.shopee_search_suggestions import scrape_shopee_search_suggestions
from app.tiki.tiki_products import scrape_tiki_products
from app.tiki.tiki_to_mongodb import tiki_to_mongo

if __name__ == '__main__':
    db_url = os.environ.get('MONGO_URL')
    # directory = 'vi-wordnet'
    # args = [(scrape_lazada_multiple, ('https://lazada.vn/', directory)),
    #         (scrape_shopee_multiple, ('https://shopee.vn/', directory)),
    #         (scrape_tiki_multiple, ('https://tiki.vn/', directory))]
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     futures = [executor.submit(f, *args_tuple) for f, args_tuple in args]
    #
    #     # Wait for all futures to complete
    #     results = [future.result() for future in concurrent.futures.as_completed(futures)]

    directory = 'mock_fast_dataset'
    scrape_tiki_search_suggestions('https://tiki.vn/', directory)
    scrape_tiki_products('https://tiki.vn/')
    tiki_to_mongo(db_url)
