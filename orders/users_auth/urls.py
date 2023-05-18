from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from django.urls import path, include
from .views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'details', viewset=UserDetailsSet, basename='user_details')
router.register(r'register', viewset=UserRegister, basename='user_register')


urlpatterns = [
    path('confirm', EmailConfirmation.as_view(), name='user_confirmation'),
    path('login', UserLogin.as_view(), name='user_login'),
    path('', include(router.urls)),
    path('password_reset', MyResetPasswordRequestToken.as_view(), name='password_reset'),
    path('password_reset/confirm', MyResetPasswordConfirm.as_view(), name='password_reset_confirm')
]
