from django.contrib import admin

from .models import Payment, SubPlan, Subscription

admin.site.register(SubPlan)
admin.site.register(Subscription)
admin.site.register(Payment)
