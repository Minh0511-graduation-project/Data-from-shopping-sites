import concurrent.futures
from lazada.lazada import scrape_lazada
from shopee.shopee import scrape_shopee
from tiki.tiki import scrape_tiki


def print_log():
    print('Start scraping')


if __name__ == '__main__':
    directory = 'vi-wordnet'
    args = [(scrape_lazada, 'https://www.lazada.vn/'), (scrape_shopee, 'https://shopee.vn/'),
            (scrape_tiki, 'https://tiki.vn/')]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(f, arg) for f, arg in args]

        # Wait for all futures to complete
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
