from django.urls import path
from .views import *

urlpatterns = [
    path('user/contact', ContactView.as_view(), name='user_contact'),
    path('order', OrderView.as_view(), name='order'),
    path('basket', BasketView.as_view(), name='basket'),
    path('partner/orders', PartnerOrders.as_view(), name='partner_orders'),
    path('partner/state', PartnerState.as_view(), name='partner_state')
]
