from rest_framework.permissions import BasePermission

from subscriptions.models import Subscription


class HasActiveSubscription(BasePermission):
    """
    Allow access only if user has active subscription
    """

    message = "No active subscription!"

    def has_permission(self, request, view):
        if not Subscription.objects.filter(user=request.user, is_active=True):
            return False
        return True
