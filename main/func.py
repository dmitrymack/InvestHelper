from urllib.request import urlopen, Request
import json
import csv
import certifi
import ssl
from bs4 import BeautifulSoup
import xlrd
import datetime

CURRENCY_IMAGE = {
    'RUB': 'https://gtmarket.ru/files/rouble-lebedev.jpg',
    'USD': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Dollar_Sign.svg/1200px-Dollar_Sign.svg.png',
    'EUR': 'https://cdn-icons-png.flaticon.com/512/32/32719.png'
}

INDEXES = (('IMOEX.ME', 'IMOEX', 'RUB'), ('%5EIXIC', 'Nasdaq100', 'USD'), ('%5EGSPC', 'S&P500', 'USD'),
           ('%5EDJI', 'Dow Jones', 'USD'), ('%5ESTOXX50E', 'Eurostoxx50', 'EUR'))

BOOKMARK_IMAGES = {
    0: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdsjZoUEo-xAXFT98_2Xjctj2ZI_lEFizoBKzxsXWHEH474poBf8X1dkeLUeqA1QvDpUU&usqp=CAU",
    1: "https://pngicon.ru/file/uploads/izbrannoye.png"
}


def res_word_end(num):
    if 10 <= num % 100 <= 20 or 5 <= num % 10 <= 9 or num % 10 == 0:
        return 'результатов'
    elif num % 10 == 1:
        return 'результат'
    else:
        return 'результата'


def get_stocks_spb():
    url = "https://spbexchange.ru/ru/listing/securities/list/?csv=download"
    # req = Request(url, headers={'User-Agent': "Mozilla/5.0"})
    # resp = urlopen(req, context=ssl.create_default_context(cafile=certifi.where()))
    with open('ListingSecurityList.csv', encoding='utf-8') as f:
        cr = csv.reader(f)
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
        if not dat: break
        start += 100
        for i in dat:
            if len(i[0]) > 5 or str(i[0]).islower() or not i[1]: continue
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
    dat = set(dat)
    print(len(dat))
    c = 0
    filtered = []
    tickers = []
    for i in dat:
        c += 1
        print(c)
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

        try:
            a['price']['marketCap']['raw'] = dict(a['price']['marketCap']).get('raw', 0)
            filtered += [a]
            tickers += [a['price']['symbol']]
        except:
            continue
    return (filtered, tickers)


def get_nasdaq100():
    url = 'https://finasko.com/wp-content/uploads/2022/03/Nasdaq-100-Weight.xlsx'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req)
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(0)
    dat = []
    for i in range(1, sheet.nrows):
        dat += [(sheet.cell_value(i, 2), 'Nasdaq100')]
    return dat


def get_sandp500():
    url = 'https://finasko.com/wp-content/uploads/2022/03/Download-SP-500-Weight.xlsx'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req)
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(0)
    dat = []
    for i in range(1, sheet.nrows):
        dat += [(sheet.cell_value(i, 2), 'S&P500')]
    return dat


def get_dowjones():
    url = 'https://finasko.com/wp-content/uploads/2022/01/Dow-Jones-Companies-By-Weightage.xlsx'
    req = Request(url, headers={'User-Agent': "Magic Browser"})
    con = urlopen(req)
    xls = xlrd.open_workbook(file_contents=con.read())
    sheet = xls.sheet_by_index(0)
    dat = []
    for i in range(3, 33):
        dat += [(sheet.cell_value(i, 2), 'Dow Jones')]
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
        dat += [(sheet.cell_value(i, 1) + '.ME', 'IMOEX')]
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
        dat += [(str(i)[t:-4])]
    return dat


def get_all_indexes():
    dat = get_eurostoxx50()
    for i in range(len(dat)):
        dat[i] = (dat[i], 'Eurostoxx50')
    dat += get_nasdaq100() + get_sandp500() + get_dowjones() + get_imoex()
    return dat


def get_prices(ticker):
    now = datetime.datetime.now()
    now_ts = now.replace(tzinfo=datetime.timezone.utc).timestamp()
    year_ago_ts = str(int(now_ts - 31536000))
    now_ts = str(int(now_ts))
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={year_ago_ts}&period2={now_ts}&interval=1d"
    resp = urlopen(url)
    a = json.loads(resp.read())['chart']['result'][0]
    a = zip(a['timestamp'], a['indicators']['quote'][0]['close'])
    dat = []
    n = 0
    for i, j in a:
        if j is not None:
            n = j
        d = datetime.datetime.utcfromtimestamp(i).strftime('%d-%m-%Y')
        dat += [(d, n)]
    return dat