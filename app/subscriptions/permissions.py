import ipaddress

from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Payment, Subscription


class HasNoActiveSubscription(BasePermission):
    """
    Allow access only if the user has no active subscription
    """

    message = "You already have active subscription"

    def has_permission(self, request, view):
        if Subscription.objects.filter(user=request.user, is_active=True):
            return False
        return True


class IsSubscriptionNotPaid(BasePermission):
    """
    Allow access only if the subscription isn't already paid
    """

    message = "This subscription is already paid for"

    def has_permission(self, request, view):
        subscription_pk = view.kwargs.get("subscription_pk")
        subscription = get_object_or_404(Subscription, pk=subscription_pk)
        if Payment.objects.filter(
            # user=request.user,
            subscription=subscription,
            status__in=[Payment.PROCESSING, Payment.COMPLETED],
        ):
            return False
        return True


class IsYookassaIP(BasePermission):
    """Allow access only to list of yokassa IPs"""

    message = "Your IP address is not allowed!"

    YOOKASSA_IP_ADDRESSES = [
        "185.71.76.0/27",
        "185.71.77.0/27",
        "77.75.153.0/25",
        "77.75.156.11",
        "77.75.156.35",
        "77.75.154.128/25",
        "2a02:5180::/32",
    ]

    def has_permission(self, request, view):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            # Extract the IP
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            # If no x_forwarder_for take REMOTE_ADDR
            ip = request.META.get("REMOTE_ADDR")

        return any(
            ipaddress.ip_address(ip) in ipaddress.ip_network(net)
            for net in self.YOOKASSA_IP_ADDRESSES
        )
