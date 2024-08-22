from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import SubPlan, Subscription


class SubPlanReadSerializer(ModelSerializer):
    """Serializer to read SubPlan"""

    discounted_price = SerializerMethodField()

    class Meta:
        model = SubPlan
        fields = (
            "id",
            "name",
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
    """Serializer to read, update (auto_new), delete Subcription"""

    plan = SerializerMethodField()

    class Meta(SubPlanReadSerializer.Meta):
        read_only_fields = SubscriptionCreateSerializer.Meta.read_only_fields + (
            "plan",
        )

    def get_plan(self, obj):
        return SubPlanReadSerializer(
            obj.plan, fields=("id", "name", "description")
        ).data
