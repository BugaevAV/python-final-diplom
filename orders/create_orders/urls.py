from django.urls import path, include
from .views import *


from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'partner/state', viewset=PartnerStateSet, basename='partner_state')

urlpatterns = [
    path('user/contact', ContactView.as_view(), name='user_contact'),
    path('order', OrderView.as_view(), name='order'),
    path('basket', BasketView.as_view(), name='basket'),
    path('partner/orders', PartnerOrders.as_view(), name='partner_orders'),
    # path('partner/state', PartnerState.as_view(), name='partner_state'),
    path('', include(router.urls)),
]
