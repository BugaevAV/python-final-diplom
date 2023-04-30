from django.urls import path
from .views import *

urlpatterns = [
    path('user/contact', ContactView.as_view(), name='user_contact'),
]
