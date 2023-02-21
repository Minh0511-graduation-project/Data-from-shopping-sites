import concurrent.futures
from app.lazada.lazada_multiple import scrape_lazada_multiple
from app.tiki.tiki_multiple import scrape_tiki_multiple
from app.shopee.shopee_multiple import scrape_shopee_multiple
from app.tiki.tiki_products import scrape_tiki_products

if __name__ == '__main__':
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
    scrape_tiki_products('https://tiki.vn/')
