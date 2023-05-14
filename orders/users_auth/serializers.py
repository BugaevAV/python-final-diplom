from rest_framework import serializers
from .models import *
from create_orders.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone', 'user')
        read_only_fields = ('id', )
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'password', 'email', 'company', 'position', 'contacts', 'type')
        read_only_fields = ('id', )
