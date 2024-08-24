from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import SubPlan, Subscription


class SubPlanBriefSerializer(ModelSerializer):
    """Concise serializer for sub plan"""

    class Meta:
        model = SubPlan
        fields = ("id", "name")


class SubPlanReadSerializer(SubPlanBriefSerializer):
    """Serializer to read SubPlan"""

    discounted_price = SerializerMethodField()

    class Meta(SubPlanBriefSerializer.Meta):
        fields = SubPlanBriefSerializer.Meta.fields + (
            "description",
            "duration_months",
            "price",
            "yearly_discount",
            "discounted_price",
        )

    def get_discounted_price(self, obj):
        return obj.get_discounted_price()


class SubscriptionCreateSerializer(ModelSerializer):
    """Serializer to create Subcription"""

    class Meta:
        model = Subscription
        fields = (
            "id",
            "plan",
            "auto_renew",
            "is_active",
            "start_date",
            "end_date",
        )
        read_only_fields = ("id", "start_date", "end_date", "is_active")


class SubscriptionSerializer(SubscriptionCreateSerializer):
    """Serializer to read, update (auto_renew), delete Subscription"""

    plan = SubPlanBriefSerializer(read_only=True)


class YookassaPaymentCreateSerializer(serializers.Serializer):
    """Serializer to create yookassa payment"""

    return_url = serializers.URLField()
