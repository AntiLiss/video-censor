from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SubPlan(models.Model):
    """Subscription plan model"""

    DURATION_MONTHS = ((1, "1 month"), (12, "12 months"))

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_months = models.IntegerField(choices=DURATION_MONTHS)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(1)]
    )
    yearly_discount = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        """Get the price after discount"""
        if self.duration_months == 12:
            return self.price - (self.price / 100 * self.yearly_discount)
        return self.price


class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    plan = models.ForeignKey(SubPlan, null=True, on_delete=models.SET_NULL)
    auto_renew = models.BooleanField(blank=True, default=False)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(blank=True, default=date.today)
    end_date = models.DateField(blank=True)

    def clean(self):
        # Limit number of active subs per user
        if self.is_active and Subscription.objects.filter(
            user=self.user,
            is_active=True,
        ).exclude(pk=self.pk):
            msg = "User can have only 1 active subscription!"
            raise ValidationError(msg)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.__get_end_date()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __get_end_date(self):
        return self.start_date + relativedelta(months=self.plan.duration_months)

    def is_current(self):
        """Check is the subscription currently active"""
        today = date.today()
        return self.is_active and self.start_date <= today < self.end_date

    def renew_period(self):
        """Renew the subscription when it expires"""
        if self.auto_renew:
            self.start_date = self.end_date
            self.end_date = self.__get_end_date()


# class Payment(models.Model):
#     pass
