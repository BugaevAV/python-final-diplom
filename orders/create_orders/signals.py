from django.dispatch import Signal, receiver
from .tasks import new_order_confirm_email


order_is_created = Signal()


@receiver(order_is_created)
def new_order(user_id, order_id, **kwargs):
    new_order_confirm_email.delay(user_id=user_id, order_id=order_id)
