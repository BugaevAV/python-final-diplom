from django.dispatch import Signal, receiver
from django_rest_passwordreset.signals import reset_password_token_created
from .tasks import *


user_is_registered = Signal()


@receiver(user_is_registered)
def user_is_registered_signal(user_id, **kwargs):
    email_confirmation_token.delay(user_id=user_id)


@receiver(reset_password_token_created)
def reset_token_created(reset_password_token, **kwargs):
    email = reset_password_token.user.email
    user = reset_password_token.user.__str__()
    key = reset_password_token.key
    email_reset_password_token.delay(user=user, key=key, email=email)
