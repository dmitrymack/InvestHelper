from urllib.request import urlopen
import json
import csv
import certifi
import ssl


def get_stocks_spb():
    url = "https://spbexchange.ru/ru/listing/securities/list/?csv=download"
    resp = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    lines = [l.decode('utf-8') for l in resp.readlines()]
    cr = csv.reader(lines)
    dat = []
    normal_list = []
    for i in cr:
        s = ''
        for j in i:
            s += j
        normal_list.append(s.split(';'))
    for i in normal_list:
        if ' ' in i[6]: i[6] = i[6].replace(' ', '-')

        if i[5].startswith('Акции иностранного'):
            dat += [i[6]]
        elif i[5].startswith('Акции обыкновенные'):
            dat += [str(i[6]) + '.ME']
    return dat


def get_stocks_moex():
    start = 0
    shdat = []
    while 1:
        resp = urlopen(
            f"https://iss.moex.com/iss/securities.json?group_by=type&group_by_filter=common_share&q=RU&iss.meta=off&securities.columns=secid,marketprice_boardid&start={start}")
        dat = json.loads(resp.read())
        dat = dat['securities']['data']
        if (not dat): break
        start += 100
        for i in dat:
            if len(i[0]) > 4 or str(i[0]).islower() or not i[1]: continue
            shdat += [str(i[0]) + '.ME']
    return shdat


def get_stock_info(ticker: str):
    try:
        resp = urlopen(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics,price")
    except:
        return
    dat = json.loads(resp.read())
    return dat['quoteSummary']['result'][0]


def filter_stocks():
    dat = get_stocks_spb() + get_stocks_moex()
    print(*dat, sep='\n')
    filtered = []
    for i in dat:
        try:
            resp = urlopen(
                f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{i}?modules=defaultKeyStatistics,price")
        except:
            continue
        a = json.loads(resp.read())
        a = a['quoteSummary']['result'][0]
        try:
            b = a['price']['regularMarketPrice']['raw']
            if a['price']['regularMarketPrice']['raw'] == 0: raise
        except:
            continue
        filtered += [i]
    return filtered
