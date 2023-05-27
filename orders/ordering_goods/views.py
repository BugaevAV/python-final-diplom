from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from django.db.models import Q
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from .models import *
from .tasks import price_loader


@extend_schema(tags=['Поставщики'])
class CategoryView(ListAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(tags=['Поставщики'])
class ShopView(ListAPIView):
    permission_classes=[IsAuthenticated]
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


@extend_schema(tags=['Поставщики'])
class ProductInfoView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        if shop_id:
            query = query & Q(shop_id=shop_id)
        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()
        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


@extend_schema(tags=['Поставщики'])
@extend_schema_view(
    post=extend_schema(summary='Обновление прайса поставлщика',
                       examples=[OpenApiExample("Пример запроса",
                                                description="Ссылка на прайс поставщика. Файл в ямл формате",
                                                value={'url': 'https://raw.githubusercontent.com/BugaevAV/python-final-diplom/vers_1/data/shop1.yaml'},
                                                status_codes=[str(status.HTTP_201_CREATED)])]))
class PartnerUpdateAPIVIew(CreateAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'status': False, 'Error': 'Только для магазинаов'}, status=403)
        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({'status': False, 'Error': str(e)})
            else:
                user_id = request.user.id
                price_loader.delay(url, user_id)
                return Response({'status': True})
        return Response({'status': False, 'Error': 'Не все необходимые параметры указаны'})
