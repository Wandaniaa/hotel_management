# Generated by Django 5.0 on 2024-09-29 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0016_checkout_tamu_checkout_alter_checkout_total_harga'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='tamu_checkout',
        ),
    ]
