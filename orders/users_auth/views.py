from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import UserSerializer
from .signals import user_is_registered
from .models import ConfirmEmailToken


class UserRegister(APIView):
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            errors = {}
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                errors_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    errors_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': errors_array}})
            else:
                request.data._mutable = True
                request.data.update({})
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    user_is_registered.send(sender=self.__class__, user_id=user.id)
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все аргуменыт'})


class EmailConfirmation(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({'status': True})
            else:
                return JsonResponse({'status': False, 'Errors': 'Не верно указан токен и(или) email'})
        return JsonResponse({'status': False, 'Errors': 'Не все обязательные параметры указаны'})


class UserLogin(APIView):
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'status': True, 'Token': token.key})
            return JsonResponse({'status': False, 'Errors': 'Ну удалось авторизвать пользователя'})
        return JsonResponse({'status': False, 'Errors': 'Не указаны все необходимые агрумены'})


class UserDetails(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Errors': 'Необходимо авторизоваться'})
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Errors': 'Необходимо авторизоваться'})
        if 'password' in request.data:
            errors = {}
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                errors_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    errors_array.append(item)
                return JsonResponse({'status': False, 'Errors': {'password': errors_array}})
            else:
                request.user.set_password(request.data['password'])

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'Errors': serializer.errors})
