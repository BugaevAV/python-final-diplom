from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from django.urls import path
from .views import *

urlpatterns = [
    path('user/register', UserRegister.as_view(), name='user_registration'),
    path('user/confirm', EmailConfirmation.as_view(), name='user_confirmation'),
    path('user/login', UserLogin.as_view(), name='user_login'),
    path('user/details', UserDetails.as_view(), name='user_details'),
    path('user/password_reset', reset_password_request_token, name='password_reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password_reset_confirm')
]
