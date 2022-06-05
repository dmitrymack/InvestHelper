from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render
from urllib.request import urlopen
import json
from .func import get_stock_info, filter_stocks, CURRENCY_IMAGE, INDEXES, get_all_indexes, BOOKMARK_IMAGES, res_word_end
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
    st = ''
    try:
        st = mdl.Stock.objects.get(ticker=ticker)
    except mdl.Stock.DoesNotExist:
        raise Http404
    except mdl.Stock.MultipleObjectsReturned:
        pass
    dat = get_stock_info(ticker)
    ind = mdl.Index.objects.filter(stock__ticker=ticker)
    if len(ind) == 0:
        ind = 0

    bkm = 0
    try:
        mdl.Bookmark.objects.get(stock__ticker=ticker, user__id=request.user.id)
        bkm = 1
    except mdl.Bookmark.DoesNotExist:
        pass

    if request.method == 'POST':
        print(st)
        print('afs')
        comm = request.POST.get('comm')
        c = mdl.Comment.objects.create(
            comment=comm,
            user=request.user,
        )
        c.stock.add(st)

    comments = mdl.Comment.objects.filter(stock__ticker=ticker).order_by('-id')

    return render(request, "main/stock.html", context={
        "ticker": ticker,
        "price": dat['price']['regularMarketPrice']['raw'],
        "price_open": dat['price']['regularMarketOpen']['raw'],
        "change": dat['price']['regularMarketChange']['fmt'],
        "change_perc": dat['price']['regularMarketChangePercent']['fmt'],
        "name": dat['price']['shortName'],
        "cur": dat['price']['currency'],
        "divs": dat['defaultKeyStatistics']['lastDividendValue']['raw']
            if 'raw' in dat['defaultKeyStatistics']['lastDividendValue'] else 0,
        "div_date": dat['defaultKeyStatistics']['lastDividendDate']['fmt']
            if 'fmt' in dat['defaultKeyStatistics']['lastDividendDate'] else '-',
        "low": dat['price']['regularMarketDayLow']['raw'],
        "high": dat['price']['regularMarketDayHigh']['raw'],
        "beta": dat['defaultKeyStatistics']['beta']['fmt'],
        "net_inc": dat['defaultKeyStatistics']['netIncomeToCommon']['raw'],
        "PE": dat['defaultKeyStatistics']['forwardPE']['fmt']
            if 'fmt' in dat['defaultKeyStatistics']['forwardPE'] else '-',
        "cap": dat['price']['marketCap']['raw'],
        "ind": ind,
        "img": BOOKMARK_IMAGES[bkm],
        "comm": comments
    })


def search_view(request):
    res = request.GET.get('s')
    queryset = mdl.Stock.objects.filter(
        Q(ticker__icontains=res) | Q(name__icontains=res),
    ).order_by('ticker')
    res_word = res_word_end(len(queryset))
    return render(request, "main/search_result.html", context={
        'stocks': queryset,
        'count': len(queryset),
        'search': res,
        'image': CURRENCY_IMAGE,
        'word': res_word
    })


def all_view(request):
    queryset = mdl.Stock.objects.all().order_by('ticker')
    res_word = res_word_end(len(queryset))
    return render(request, "main/search_result.html", context={
        'stocks': queryset,
        'count': len(queryset),
        'image': CURRENCY_IMAGE,
        'word': res_word
    })


def bookmark(request, ticker):
    user = request.user
    stock = mdl.Stock.objects.get(ticker=ticker)
    resp = 0
    try:
        bk = mdl.Bookmark.objects.get(stock__ticker=ticker, user__id=user.id)
        bk.delete()
    except mdl.Bookmark.DoesNotExist:
        mdl.Bookmark.objects.create(
            user=user,
            stock=stock
        )
        resp = 1
    return JsonResponse({'resp': resp})


@login_required
def bookmark_view(request):
    queryset = mdl.Bookmark.objects.filter(user__id=request.user.id)
    qs = []
    for i in range(len(queryset)):
        qs += [queryset[i].stock]
    res_word = res_word_end(len(qs))
    return render(request, "main/search_result.html", context={
        'stocks': qs,
        'count': len(qs),
        'image': CURRENCY_IMAGE,
        'is_bkm': True,
        'word': res_word
    })


@login_required
def comments_view(request):
    queryset = mdl.Comment.objects.filter(user__id=request.user.id).order_by('-id')
    stocks = []
    for i in queryset:
        stocks += [i.stock.get()]
    print(stocks)
    return render(request, "main/comments.html", context={
        'comm': zip(queryset, stocks),
        'count': len(queryset)
    })


def custom404(request, exception):
    return HttpResponseNotFound('<h1>Ошибка 404:</h1><h2>Данной страницы не существует</h2>')


def custom500(request):
    return HttpResponseServerError('<h1>Ошибка 500:</h1><h2>К сожалению, наш сервер сломался</h2>')
