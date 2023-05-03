from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from django.urls import path
from .views import *

urlpatterns = [
    path('register', UserRegister.as_view(), name='user_registration'),
    path('confirm', EmailConfirmation.as_view(), name='user_confirmation'),
    path('login', UserLogin.as_view(), name='user_login'),
    path('details', UserDetails.as_view(), name='user_details'),
    path('password_reset', reset_password_request_token, name='password_reset'),
    path('password_reset/confirm', reset_password_confirm, name='password_reset_confirm')
]
