from celery import shared_task
from datetime import date
from .models import Subscription


@shared_task
def deactivate_expired_subscriptions():
    """Deactivate expired user subscriptions"""
    expired_subs = Subscription.objects.filter(end_date__lt=date.today())
    expired_subs.update(is_active=False)
