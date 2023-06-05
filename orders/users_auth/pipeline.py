from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from .models import User



def social_auth_login(strategy, backend, details, *args, **kwargs):
    user = User.objects.filter(username=details.get('username')).first()
    user.is_active = True
    user.save()
    token, _ = Token.objects.get_or_create(user_id=user.id)
    return JsonResponse({'Token': token.key})
