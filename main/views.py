from django.http import JsonResponse
from django.shortcuts import render
from .func import get_stock_info, filter_stocks
from .models import Stock


def get_info(request, ticker):
    response = get_stock_info(ticker)
    return JsonResponse(response)


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
        "name": dat['price']['longName'],
        "cur": dat['price']['currency']
    })


