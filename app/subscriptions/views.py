import uuid

import yookassa
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Payment, SubPlan, Subscription
from .permissions import (HasNoActiveSubscription, IsSubscriptionNotPaid,
                          IsYokassaIP)
from .serializers import (SubPlanReadSerializer, SubscriptionCreateSerializer,
                          SubscriptionSerializer,
                          YookassaPaymentCreateSerializer)


class SubPlanReadViewSet(ReadOnlyModelViewSet):
    """Read subscription plans"""

    queryset = SubPlan.objects.all()
    serializer_class = SubPlanReadSerializer


class SubscriptionViewSet(ModelViewSet):
    """CRUD subscriptions"""

    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        if self.action == "create":
            return [p() for p in self.permission_classes] + [
                HasNoActiveSubscription(),
            ]
        return super().get_permissions()

    def get_queryset(self):
        # Limit subscriptions to this user
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        # Change serializer based on action
        if self.action == "create":
            return SubscriptionCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # Set this user to user field
        serializer.save(user=self.request.user)


class PaymentCreateView(APIView):
    """Create Payment instance and yookassa payment"""

    permission_classes = [IsAuthenticated, IsSubscriptionNotPaid]
    serializer_class = YookassaPaymentCreateSerializer

    def post(self, request, subscription_pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return_url = serializer.validated_data.get("return_url")
        # Limit payable subscriptions to the current user
        personal_subs = Subscription.objects.filter(user=request.user)
        subscription = get_object_or_404(personal_subs, pk=subscription_pk)
        total_amount = subscription.plan.get_discounted_price()

        # Create Payment instance
        payment = Payment.objects.create(
            subscription=subscription,
            amount=total_amount,
        )
        try:
            # Create yookassa payment
            yk_payment = yookassa.Payment.create(
                {
                    # TODO: Include commission to amount
                    "amount": {
                        "value": total_amount,
                        "currency": "RUB",
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": return_url,
                    },
                    "capture": True,
                    "description": f'Payment for "{subscription.plan.name}"',
                    "metadata": {
                        "payment_pk": payment.pk,
                        "subscription_pk": subscription.pk,
                    },
                },
                uuid.uuid4(),
            )
            data = {"confirmation_url": yk_payment.confirmation.url}
            return Response(data, 201)
        except Exception as e:
            payment.status = payment.FAILED
            payment.save()
            return Response({"detail": str(e)}, 500)


class YookassaWebhookView(APIView):
    """
    Modify subscription and payment based on yookassa payment status
    """

    permission_classes = [IsYokassaIP]

    def post(self, request):
        payment_pk = request.data["object"]["metadata"]["payment_pk"]
        subscription_pk = request.data["object"]["metadata"]["subscription_pk"]

        payment = get_object_or_404(Payment, pk=payment_pk)
        subscription = get_object_or_404(Subscription, pk=subscription_pk)

        # Complete payment and subscription if yokassa payment was successful
        if request.data["event"] == "payment.succeeded":
            payment.status = payment.COMPLETED
            payment.payment_method = request.data["object"]["payment_method"]["type"]
            subscription.is_active = True
        # Mark payment as failed if yokassa payment was canceled
        elif request.data["event"] == "payment.canceled":
            payment.status = payment.FAILED

        payment.save()
        subscription.save()

        return Response(status=200)
