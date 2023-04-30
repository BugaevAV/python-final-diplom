from django.http import JsonResponse
from django.db.models import Q, F, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from users_auth.serializers import ContactSerializer
from .models import Contact


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











