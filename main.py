import concurrent.futures
from lazada.lazada import scrape_lazada
from shopee.shopee import scrape_shopee
from tiki.tiki import scrape_tiki


def print_log():
    print('Start scraping')


if __name__ == '__main__':
    directory = 'vi-wordnet'
    print_log()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(scrape_lazada, 'https://www.lazada.vn/')
        executor.submit(scrape_shopee, 'https://shopee.vn/')
        executor.submit(scrape_tiki, 'https://tiki.vn/')

        concurrent.futures.wait([scrape_lazada, scrape_shopee, scrape_tiki])
