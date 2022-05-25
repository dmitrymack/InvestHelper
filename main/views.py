from django.http import JsonResponse
from django.shortcuts import render
from urllib.request import urlopen
import json
from .func import get_stock_info, filter_stocks
from .models import Stock


def get_info(request, ticker):
    response = get_stock_info(ticker)
    return JsonResponse(response)


def get_cur_courses(request):
    resp = urlopen('https://www.cbr-xml-daily.ru/daily_json.js')
    dat = json.loads(resp.read())
    dat['Valute']['USD']['Value'] = round(dat['Valute']['USD']['Value'], 2)
    dat['Valute']['EUR']['Value'] = round(dat['Valute']['EUR']['Value'], 2)
    dat['Valute']['GBP']['Value'] = round(dat['Valute']['GBP']['Value'], 2)
    dat['Valute']['CNY']['Value'] = round(dat['Valute']['CNY']['Value'] / 10, 2)
    dat['Valute']['JPY']['Value'] = round(dat['Valute']['JPY']['Value'] / 100, 2)
    return JsonResponse(dat['Valute'])


def fill_base(request):
    dat = filter_stocks()
    for i in dat:
        Stock.objects.create()
    return render(request, "main/index.html")


def main_view(request):

    return render(request, "main/index.html")


def stock_view(request, ticker):
    dat = get_stock_info(ticker)
    return render(request, "main/stock.html", context={
        "ticker": ticker,
        "price": dat['price']['regularMarketPrice']['raw'],
        "name": dat['price']['shortName'],
        "cur": dat['price']['currency']
    })


