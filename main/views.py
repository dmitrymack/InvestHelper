from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from urllib.request import urlopen
import json
import csv
import certifi
import ssl



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
            shdat += [i[0]]
    return shdat


def get_stocks_spb():
    url = "https://spbexchange.ru/ru/listing/securities/list/?csv=download"
    resp = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
    lines = [l.decode('utf-8') for l in resp.readlines()]
    cr = csv.reader(lines)



def get_stock_info(ticker: str):
    print(ticker, end=':  ')
    try:
        resp = urlopen(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=defaultKeyStatistics,price")
    except:
        return
    dat = json.loads(resp.read())
    return dat['quoteSummary']['result'][0]['price']['regularMarketPrice']

def get_info(request, ticker):
    response = get_stock_info(ticker)
    return JsonResponse(response)


def main_view(request):

    # dat = get_stocks_moex()
    # print(dat)
    # print(len(dat))
    # for i in dat:
    #     get_stock_info(i)
    #     pass
    # print()
    return render(request, "main/index.html")


def stock_view(request, ticker):
    return render(request, "main/stock.html", context={"ticker": ticker})


