import requests
import json
import calendar
import time
from multiprocessing.pool import ThreadPool


def get_cats():
    lst = []
    with open('cats.txt') as infile:
        for line in infile:
            cat, _ = line.split('\t')
            lst.append(cat)
    return lst


url = 'http://export.arxiv.org/api/query?search_query=cat:{}+AND+submittedDate:[{}0000+TO+{}0000]&max_results=2000'


def display_date(date):
    y, m, d = date
    year_ = str(y)
    month_ = str(m)
    if m < 10:
        month_ = '0' + month_
    date_ = str(d)
    if d < 10:
        date_ = '0' + date_
    return year_+month_+date_


def get_content_from_month(tuple_):
    cat, y, m = tuple_
    month_start = (y, m, 1)
    _, end = calendar.monthrange(y, m)
    month_end = (y, m, end)
    n = 0
    resp = None
    while n < 10:
        n += 1
        try:
            resp = requests.get(url.format(cat, display_date(month_start), display_date(month_end)), timeout=60.0)
        except IOError as error:
            print(error)
            time.sleep(1)
            continue

        if not resp:
            continue

        if resp.status_code == 200:
            break

        time.sleep(1)

    if resp.status_code == 200:
        print('good with ({}, {}, {})'.format(cat, y, m))
        text = resp.text
        if '<summary>' in text:
            return [[cat, y, m], text]
        return None
    print('bad with ({}, {})'.format(cat, y, m))
#

if __name__ == '__main__':
    months = list(range(1, 13))

    cats = get_cats()
    for year in range(2000, 2017):
        all_args = [(cat, y, m) for cat in cats for y in [year] for m in months]
        pool = ThreadPool(50)
        lst = pool.map(get_content_from_month, all_args)
        json.dump(list(filter(lambda x: x is not None, lst)), open('arxiv_dump_{}.json'.format(year), 'w'))









