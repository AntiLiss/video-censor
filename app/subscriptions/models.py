from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SubPlan(models.Model):
    """Subscription plan model"""

    # Duration of subscription plan in months
    DURATION_CHOICES = ((1, "1 month"), (12, "12 months"))

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_months = models.IntegerField(choices=DURATION_CHOICES)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    yearly_discount = models.DecimalField(
        blank=True,
        null=True,
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        """Get the price after discount"""
        if self.duration_months == 12:
            final_price = self.price - (self.price / 100 * self.yearly_discount)
            return f"{final_price:.2f}"
        return self.price


class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    plan = models.ForeignKey(SubPlan, null=True, on_delete=models.SET_NULL)
    auto_renew = models.BooleanField(blank=True, default=False)
    is_active = models.BooleanField(default=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Limit number of active subs per user
        if self.is_active and Subscription.objects.filter(
            user=self.user,
            is_active=True,
        ).exclude(pk=self.pk):
            msg = "User can have only 1 active subscription!"
            raise ValidationError(msg)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def start_period(self):
        """Set subscription as active and set dates"""
        self.is_active = True
        self.start_date = date.today()
        self.end_date = self.start_date + relativedelta(
            months=self.plan.duration_months
        )


class Payment(models.Model):
    """Payment model"""

    # Status choices
    PROCESSING = "P"
    COMPLETED = "C"
    FAILED = "F"

    STATUS_CHOICES = (
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    )

    subscription = models.ForeignKey(
        Subscription,
        null=True,
        on_delete=models.SET_NULL,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="RUB")
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=PROCESSING,
        blank=True,
    )
    payment_method = models.CharField(max_length=250, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
