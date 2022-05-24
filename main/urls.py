from django.urls import path
import main.views as view

urlpatterns = [
    path('', view.main_view, name='main'),
    path('stock/<str:ticker>', view.stock_view, name='stock'),
    path('get_info/<str:ticker>', view.get_info, name='info'),
]