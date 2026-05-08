import os
from bs4 import BeautifulSoup
import requests
import datetime
from da_design_server.src import mylogger, myconfig
import pdb

def crawl_stock(logger, limit=30):
    """Collect data from a copy webpage of NPay kospi, and return data pairs.

    :param logger: logger instance
    :type logger: logging.Logger
    :param limit: maximum # of items (default 30), NEVER > 30 because this is just a copy webpage
    :type limit: int
    :return: pairs of {company: stock}
    :rtype: dict
    """
    url = 'http://10.255.81.97/for_class/Npay.html'

    stocks = {}

    n_got = 0 # # of current items
    page = 1 # webpage index

    if limit > 30 or limit < 0:
        limit = 30
        logger.info('Invalid #items lmit. So, it is forced to be 30, now.')
    logger.info('#items limit = {}'.format(limit))

    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')

    tr_list = soup.select('table.type_5 tbody tr')
    for tr in tr_list:
        name_tag = tr.select_one('a.tltle')
        price_tags = tr.select('td.number')

        if not name_tag or not price_tags or len(price_tags) <= 2:
            continue

        price = price_tags[1].get_text(strip=True).replace(',', '')
        name = name_tag.get_text(strip=True)

        stocks[name] = int(price)
        n_got += 1
        logger.info('collected: {}={}'.format(name, price))

        if n_got >= limit:
            break

    logger.info('{} items collected.'.format(n_got))
    return stocks

if __name__ == '__main__':
    project_root_path = os.getenv("DA_DESIGN_SERVER")
    cfg = myconfig.get_config('{}/share/project.config'.format(project_root_path))
    log_path = cfg['logger'].get('log_directory')
    logger = mylogger.get_logger(log_path)
    ret = crawl_stock(logger)
