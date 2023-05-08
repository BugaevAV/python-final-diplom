from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from orders.celery import app
from .models import ConfirmEmailToken


@app.task
def email_confirmation_token(user_id):
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    msg = EmailMultiAlternatives(
        # заголовок письма:
        f"Токен для подверждения электронной почты {token.user.email}",
        # сообщение получателю - токен:
        token.key,
        # адрес отправителя:
        settings.EMAIL_HOST_USER,
        # адрес получателя:
        [token.user.email]
    )
    msg.send()


@app.task
def email_reset_password_token(user, key, email):
    msg = EmailMultiAlternatives(
        # заголовок письма:
        f"Токен для сброса пароля для {user}",
        # сообщение получателю - токен:
        key,
        # адрес отправителя:
        settings.EMAIL_HOST_USER,
        # адрес получателя:
        [email]
    )
    msg.send()
