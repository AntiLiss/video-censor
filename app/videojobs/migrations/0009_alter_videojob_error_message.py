# Generated by Django 5.0.8 on 2024-08-17 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videojobs', '0008_videojob_error_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videojob',
            name='error_message',
            field=models.TextField(blank=True, default='test'),
            preserve_default=False,
        ),
    ]
