# Generated by Django 5.0 on 2024-10-27 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0019_checkout_sisa_pembayaran_checkout_status_pembayaran'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='status_checkout',
            field=models.BooleanField(default=False),
        ),
    ]
