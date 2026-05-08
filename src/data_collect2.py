import os
from bs4 import BeautifulSoup
import requests
import datetime
from pymongo import MongoClient
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

def save_to_db(logger, stock_pairs):
    """Put the given {company: stock} pairs into DB

    :param logger: logger instance
    :type logger: logging.Logger
    :param stock_pairs: {company: stock} pairs
    :type stock_pairs: dict
    """
    today = datetime.date.today()
    today = datetime.datetime(today.year, today.month, today.day)

    for company in stock_pairs.keys():
        # Insert the company data if not exists.
        doc_company = col_company.find_one({'name': company})
        if not doc_company:
            col_company.insert_one({
                'name': company,
                'company_stock': []
            })
            doc_company = col_company.find_one({'name': company})
        company_id = doc_company['_id']

        # Insert stock value of today if not exists.
        doc_company_stock = col_company.find_one({
            '_id': company_id, 'company_stock.date': today})
        if not doc_company_stock:
            col_company.update_one(
                {"_id": company_id},
                {"$push": {
                    'company_stock': {
                        'date': today,
                        'value': float(stock_pairs[company])
                    }
                }
                }
            )
            logger.info('{} {}: new item in DB = {}'.format(
                today, company, stock_pairs[company]))
        else:
            logger.info('{} {}: already exist, so skipped.'.format(
                today, company))

def show_db(logger, limit=10):
    """Show company-related data in DB.

    :param logger: logger instance
    :type logger: logging.Logger
    :param limit: maximum # of items to show
    :type limit: int
    """
    for i, d in enumerate(col_company.find({})):
        if i == limit:
            break
        logger.info('DB(Company): {} {}'.format(
            d['name'], d['company_stock']))

if __name__ == '__main__':
    project_root_path = os.getenv("DA_DESIGN_SERVER")
    cfg = myconfig.get_config('{}/share/project.config'.format(project_root_path))
    log_path = cfg['logger'].get('log_directory')
    logger = mylogger.get_logger(log_path)

    ret = crawl_stock(logger)

    print('{} data collected.'.format(len(ret)))
    if not ret:
        exit()
    print('Top data instances:')
    for i, x in enumerate(ret.items()):
        logger.info('{}'.format(x))
        if i >= 10:
            break

    db_ip = cfg['db']['ip']
    db_port = int(cfg['db']['port'])
    db_name = cfg['db']['name']

    db_client = MongoClient(db_ip, db_port)
    db = db_client[db_name]

    col_company = db[cfg['db']['col_company']]

    # DB에 입력하기 전
    logger.info('DB status (before)')
    show_db(logger)

    # DB 입력
    logger.info('Saving to DB ----------------------')
    save_to_db(logger, ret)
    logger.info('----------------------  Saved to DB')

    # DB에 입력한 후
    logger.info('DB status (after)')
    show_db(logger)
