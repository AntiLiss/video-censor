# Generated by Django 5.0.8 on 2024-08-25 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0011_alter_payment_amount_alter_payment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
