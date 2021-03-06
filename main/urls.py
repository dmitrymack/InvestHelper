from django.urls import path
import main.views as view

urlpatterns = [
    path('', view.main_view, name='main'),
    path('stock/<str:ticker>', view.stock_view, name='stock'),
    path('get_info/<str:ticker>', view.get_info, name='info'),
    path('get_courses', view.get_cur_courses, name='courses'),
    path('search', view.search_view, name='search'),
    path('index/<str:index>', view.index_view, name='index'),
    path('all_stocks', view.all_view, name='all'),
    path('bookmark/<str:ticker>', view.bookmark, name='bookmark'),
    path('my_bookmarks', view.bookmark_view, name='my_bkm'),
    path('my_comments', view.comments_view, name='my_comm'),
]

handler404 = view.custom404
handler500 = view.custom500