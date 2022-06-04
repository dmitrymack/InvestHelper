from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render
from urllib.request import urlopen
import json
from .func import get_stock_info, filter_stocks, CURRENCY_IMAGE, INDEXES, get_all_indexes
import main.models as mdl


def get_info(request, ticker):
    response = get_stock_info(ticker)
    return JsonResponse(response)


def fill_indexes(request):
    for i in INDEXES:
        try:
            mdl.Index.objects.get(name=i[1])
        except mdl.Index.DoesNotExist:
            mdl.Index.objects.create(
                indexTicker=i[0],
                name=i[1],
                currency=i[2],
                price=0
            )

    dat = get_all_indexes()
    for i in dat:
        try:
            ind = mdl.Index.objects.get(name=i[1])
            st = mdl.Stock.objects.get(ticker=i[0])
        except:
            continue

        try:
            ind_st = mdl.Index.objects.get(name=ind.name, stock__ticker=st.ticker)
        except mdl.Index.DoesNotExist:
            ind.stock.add(st)
    return JsonResponse({'status': 'OK'})


def get_cur_courses(request):
    resp = urlopen('https://www.cbr-xml-daily.ru/daily_json.js')
    dat = json.loads(resp.read())
    dat = dat['Valute']
    dat['USD']['Value'] = round(dat['USD']['Value'] / dat['USD']['Nominal'], 2)
    dat['EUR']['Value'] = round(dat['EUR']['Value'] / dat['EUR']['Nominal'], 2)
    dat['GBP']['Value'] = round(dat['GBP']['Value'] / dat['GBP']['Nominal'], 2)
    dat['CNY']['Value'] = round(dat['CNY']['Value'] / dat['CNY']['Nominal'], 2)
    dat['JPY']['Value'] = round(dat['JPY']['Value'] / dat['JPY']['Nominal'], 2)
    return JsonResponse(dat)


def fill_base(request):
    dat = filter_stocks()
    c = 0
    for i in dat[0]:
        c += 1
        print("URA " + str(c))

        mdl.Stock.objects.update_or_create(
            ticker=i['price']['symbol'],
            name=i['price']['shortName'],
            dailyLow=i['price']['regularMarketDayLow']['raw'],
            dailyHigh=i['price']['regularMarketDayHigh']['raw'],
            currency=i['price']['currency'],
            cap=i['price']['marketCap']['raw'],
        )

    # st = mdl.Stock.objects.all()
    # for i in st:
    #     if i.ticker not in dat[1]:
    #         i.delete()

    return render(request, "main/index.html")


def main_view(request):
    queryset = []
    queryset += [mdl.Index.objects.get(name='IMOEX').stock.order_by('-cap')[:10]]
    queryset += [mdl.Index.objects.get(name='S&P500').stock.order_by('-cap')[:10]]
    queryset += [mdl.Index.objects.get(name='Nasdaq100').stock.order_by('-cap')[:10]]
    queryset += [mdl.Index.objects.get(name='Dow Jones').stock.order_by('-cap')[:10]]
    queryset += [mdl.Index.objects.get(name='Eurostoxx50').stock.order_by('-cap')[:10]]
    ind = zip(['IMOEX', 'S&P500', 'Nasdaq100', 'Dow Jones', 'Eurostoxx50'], queryset)
    return render(request, "main/index.html", context={
        'ind': ind,
    })


def index_view(request, index):
    st = mdl.Index.objects.get(name=index).stock.order_by('-cap')
    return render(request, "main/index_stocks.html", context={
        'name': index,
        'stocks': st,
        'image': CURRENCY_IMAGE
    })


def stock_view(request, ticker):
    try:
        mdl.Stock.objects.get(ticker=ticker)
    except mdl.Stock.DoesNotExist:
        raise Http404
    except mdl.Stock.MultipleObjectsReturned:
        pass
    dat = get_stock_info(ticker)
    ind = mdl.Index.objects.filter(stock__ticker=ticker)
    if len(ind) == 0:
        ind = 0
    return render(request, "main/stock.html", context={
        "ticker": ticker,
        "price": dat['price']['regularMarketPrice']['raw'],
        "price_open": dat['price']['regularMarketOpen']['raw'],
        "change": dat['price']['regularMarketChange']['fmt'],
        "change_perc": dat['price']['regularMarketChangePercent']['fmt'],
        "name": dat['price']['shortName'],
        "cur": dat['price']['currency'],
        "divs": dat['defaultKeyStatistics']['lastDividendValue']['raw'] if 'raw' in dat['defaultKeyStatistics']['lastDividendValue'] else 0,
        "div_date": dat['defaultKeyStatistics']['lastDividendDate']['fmt'] if 'fmt' in dat['defaultKeyStatistics']['lastDividendDate'] else '-',
        "low": dat['price']['regularMarketDayLow']['raw'],
        "high": dat['price']['regularMarketDayHigh']['raw'],
        "beta": dat['defaultKeyStatistics']['beta']['fmt'],
        "net_inc": dat['defaultKeyStatistics']['netIncomeToCommon']['raw'],
        "PE": dat['defaultKeyStatistics']['forwardPE']['fmt'],
        "cap": dat['price']['marketCap']['raw'],
        "ind": ind
    })


def search_view(request):
    res = request.GET.get('s')
    queryset = mdl.Stock.objects.filter(
        Q(ticker__icontains=res) | Q(name__icontains=res),
    ).order_by('ticker')
    return render(request, "main/search_result.html", context={
        'stocks': queryset,
        'count': len(queryset),
        'search': res,
        'image': CURRENCY_IMAGE
    })


def all_view(request):
    queryset = mdl.Stock.objects.all().order_by('ticker')
    return render(request, "main/search_result.html", context={
        'stocks': queryset,
        'count': len(queryset),
        'image': CURRENCY_IMAGE
    })


def custom404(request, exception):
    return HttpResponseNotFound('<h1>Ошибка 404:</h1><h2>Данной страницы не существует</h2>')


def custom500(request):
    return HttpResponseServerError('<h1>Ошибка 500:</h1><h2>К сожалению, наш сервер сломался</h2>')
