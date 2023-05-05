from distutils.util import strtobool

import ujson
from django.http import JsonResponse
from django.db.models import Q, F, Sum
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response

from ordering_goods.models import Shop
from ordering_goods.serializers import ShopSerializer
from .models import *
from .signals import *
from .serializers import *


class ContactView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'status': True})
            else:
                return JsonResponse({'status': False, 'Error': serializer.errors})
        return JsonResponse({'status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'status': True})
                    else:
                        return JsonResponse({'status': False, 'Errors': serializer.errors})
        return JsonResponse({'status': False, 'Error': 'Не указаны все необходимые агрументы'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        items_string = request.data.get('items')
        if items_string:
            items_list = items_string.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True
            if objects_deleted:
                count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'status': True, 'Удалено контактов': count})
        return JsonResponse({'status': False, 'Error': 'Не указаны все необходимые аргумены'})


class BasketView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Необходимо авторизоваться'})
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Необходимо авторизоваться'})
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = ujson.loads(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})
                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        items_string = request.data.get('items')
        if items_string:
            try:
                items_dict = ujson.loads(items_string)
            except ValueError:
                return JsonResponse({'status': False, 'Error': 'Не верный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_update = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_update += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])
                return JsonResponse({'status': True, 'Обновлено позиций': objects_update})
        return JsonResponse({'status': False, 'Error': 'Не указаны все необходимые параметры'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        items_string = request.data.get('items')
        if items_string:
            list_items = items_string.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            deleted_positions = False
            for item_id in list_items:
                if item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=item_id)
                    deleted_positions = True
            if deleted_positions:
                deleted_positions_count = OrderItem.objects.filter(query).delete()[0]
                left_position_count = OrderItem.objects.filter(order_id=basket.id).count()
                if left_position_count == 0:
                    Order.objects.filter(state='basket', user_id=request.user.id).delete()
                    return JsonResponse({'status': True, 'Удалено объектов': f'{deleted_positions_count}. '
                                                                             f'В вашей корзине пусто!'})
                return JsonResponse({'status': True, 'Удалено объектов': deleted_positions_count})
        return JsonResponse({'status': False, 'Error': 'Не указаны все необходимые параметры'})


class OrderView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        if {'order_id', 'contact'}.issubset(request.data):
            try:
                updated = Order.objects.filter(user_id=request.user.id, id=request.data['order_id']).update(
                                               contact_id=request.data['contact'], state='new')
            except IntegrityError as error:
                return JsonResponse({'status': False, 'Error': 'Не верно указаны аругменты'})
            else:
                if updated:
                    order_is_created.send(sender=self.__class__, user_id=request.user.id,
                                          order_id=request.data['order_id'])
                    return JsonResponse({'status': True})
        return JsonResponse({'status': False, 'Error': 'Не указаны все необходимые параметры'})

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'Error': 'Необходимо авторизоваться'})
        order = Order.objects.filter(user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity')*F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class PartnerOrders(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Необходимо авторизоваться'})
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'})
        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class PartnerState(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Необходимо авторизоваться'})
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'})
        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Необходимо авторизоваться'})
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'})
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'State changed to': state})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
