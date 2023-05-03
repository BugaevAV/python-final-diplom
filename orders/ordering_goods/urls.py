from django.urls import path
from .views import *


urlpatterns = [
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('partner/update', PartnerUpdateAPIVIew.as_view(), name='update_price')
]


