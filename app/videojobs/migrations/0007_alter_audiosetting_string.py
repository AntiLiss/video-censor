# Generated by Django 5.0.8 on 2024-08-10 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videojobs', '0006_audiosetting_string'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiosetting',
            name='string',
            field=models.CharField(blank=True, default='mystring', max_length=10),
        ),
    ]
