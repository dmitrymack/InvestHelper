from urllib.request import urlopen, Request
import json
import csv
import certifi
import ssl
from bs4 import BeautifulSoup
import xlrd


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
    dat = get_stocks_moex() + get_stocks_spb() + get_eurostoxx50()
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
        a['price']['marketCap']['raw'] = dict(a['price']['marketCap']).get('raw', 0)
        filtered += [a]
        #print(f"{a['price']['symbol']} {a['price']['shortName']} {a['price']['currency']} {a['price']['regularMarketDayLow']['raw']} {a['price']['marketCap']['raw']}")
    return filtered


def get_nasdaq100():
    url = 'https://finasko.com/wp-content/uploads/2022/03/Nasdaq-100-Weight.xlsx'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req)
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(0)
    dat = []
    for i in range(1, sheet.nrows):
        dat += [sheet.cell_value(i, 2)]
    return dat


def get_sandp500():
    url = 'https://finasko.com/wp-content/uploads/2022/03/Download-SP-500-Weight.xlsx'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req)
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(0)
    dat = []
    for i in range(1, sheet.nrows):
        dat += [sheet.cell_value(i, 2)]
    return dat


def get_dowjones():
    url = 'https://finasko.com/wp-content/uploads/2022/01/Dow-Jones-Companies-By-Weightage.xlsx'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req)
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(0)
    dat = []
    for i in range(3, 33):
        dat += [sheet.cell_value(i, 2)]
    return dat


def get_imoex():
    url = 'https://fs.moex.com/files/15237'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req, context=ssl.create_default_context(cafile=certifi.where()))
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(1)
    dat = []
    for i in range(4, sheet.nrows):
        if sheet.cell_value(i, 1) == '':
            break
        dat += [sheet.cell_value(i, 1)]
    return dat


def get_eurostoxx50():
    url = 'https://finance.yahoo.com/quote/%5ESTOXX50E/components?p=%5ESTOXX50E'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req, context=ssl.create_default_context(cafile=certifi.where()))
    soup = BeautifulSoup(con.read(), 'lxml')
    quotes = soup.find_all('a', class_='C($linkColor) Cur(p) Td(n) Fw(500)')
    dat = []
    for i in quotes:
        t = str(i).find('>') + 1
        dat += [str(i)[t:-4]]
    return dat
