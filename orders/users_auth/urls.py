from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from django.urls import path, include
from .views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'details', viewset=UserDetailsSet, basename='user_details')


urlpatterns = [
    path('register', UserRegister.as_view(), name='user_registration'),
    path('confirm', EmailConfirmation.as_view(), name='user_confirmation'),
    path('login', UserLogin.as_view(), name='user_login'),
    path('', include(router.urls)),
    # path('details', UserDetails.as_view(), name='user_details'),
    path('password_reset', reset_password_request_token, name='password_reset'),
    path('password_reset/confirm', reset_password_confirm, name='password_reset_confirm')
]
