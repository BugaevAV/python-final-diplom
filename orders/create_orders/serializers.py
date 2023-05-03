from rest_framework import serializers
from create_orders.models import OrderItem
from users_auth.serializers import ContactSerializer
from create_orders.models import Order
from ordering_goods.serializers import ProductInfoSerializer


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order', )
        read_only_fields = ('id', )
        extra_kwargs = {
            'orders': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'creating_date', 'total_sum', 'contact', )
        read_only_fields = ('id', )
