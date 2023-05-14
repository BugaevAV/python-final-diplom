from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django_rest_passwordreset.views import ResetPasswordConfirm, ResetPasswordRequestToken
from .serializers import *
from .signals import user_is_registered
from .models import *

from rest_framework import viewsets, status


@extend_schema(tags=['Пользователи'], examples=[OpenApiExample(
        "Post example",
        description="Test example for the post",
        value=
        {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'salegroup78@mail.ru',
            'password': 'Ivan1234',
            'company': 'Рога&Копыта',
            'position': 'Директор',
            'type': 'shop'
        },
        status_codes=[str(status.HTTP_200_OK)],
    )], )
class UserRegister(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(self.request.data):
            errors = {}
            try:
                validate_password(self.request.data['password'])
            except Exception as password_error:
                errors_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    errors_array.append(item)
                return Response({'Status': False, 'Errors': {'password': errors_array}})
            else:
                self.request.data['password'] = make_password(self.request.data['password'])
                obj = self.create(request, *args, **kwargs)
                user_is_registered.send(sender=self.__class__, user_id=obj.data['id'])
                return obj
        return Response({'Status': False, 'Errors': 'Не указаны все аргументы'})


@extend_schema(tags=['Пользователи'], examples=[OpenApiExample(
        "Post example",
        description="Test example for the post",
        value=
        {
            'email': 'salegroup78@mail.ru',
            'token': '5d6d2b9cdcbe7e07a53cb1afd5e751b102',
        },
        status_codes=[str(status.HTTP_200_OK)],
    )], )
class EmailConfirmation(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'status': True})
            else:
                return Response({'status': False, 'Errors': 'Не верно указан токен и(или) email'})
        return Response({'status': False, 'Errors': 'Не все обязательные параметры указаны'})


class UserLogin(APIView):
    @extend_schema(tags=['Пользователи'])
    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'status': True, 'Token': token.key})
            return JsonResponse({'status': False, 'Errors': 'Ну удалось авторизвать пользователя'})
        return JsonResponse({'status': False, 'Errors': 'Не указаны все необходимые агрумены'})


# class UserDetails(APIView):
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'status': False, 'Errors': 'Необходимо авторизоваться'})
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)
#
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'status': False, 'Errors': 'Необходимо авторизоваться'})
#         if 'password' in request.data:
#             errors = {}
#             try:
#                 validate_password(request.data['password'])
#             except Exception as password_error:
#                 errors_array = []
#                 # noinspection PyTypeChecker
#                 for item in password_error:
#                     errors_array.append(item)
#                 return JsonResponse({'status': False, 'Errors': {'password': errors_array}})
#             else:
#                 request.user.set_password(request.data['password'])
#
#         serializer = UserSerializer(request.user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse({'status': True})
#         else:
#             return JsonResponse({'status': False, 'Errors': serializer.errors})

@extend_schema(tags=['Пользователи'], examples=[OpenApiExample(
                    "Post example",
                    description="Test example for the post",
                    value=
                    {
                        'password': 'Petya1234newnew'
                    },
                    status_codes=[str(status.HTTP_200_OK)],
                )], )
class UserDetailsSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Response({'status': False, 'Errors': 'Необходимо авторизоваться'})
        return User.objects.all()

    @action(detail=True, methods=['POST'])
    def change(self, request, *args, **kwargs):
        if 'password' in self.request.data:
            errors = {}
            try:
                validate_password(self.request.data['password'])
            except Exception as password_error:
                errors_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    errors_array.append(item)
                return Response({'status': False, 'Errors': {'password': errors_array}})
            else:
                self.request.user.set_password(self.request.data['password'])
        serializer = UserSerializer(self.request.user, data=self.request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True})
        else:
            return Response({'status': False, 'Errors': serializer.errors})


@extend_schema(tags=['Пользователи'])
class MyResetPasswordRequestToken(ResetPasswordRequestToken):
    pass


@extend_schema(tags=['Пользователи'])
class MyResetPasswordConfirm(ResetPasswordConfirm):
    pass
