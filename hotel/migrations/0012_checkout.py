# Generated by Django 5.0 on 2024-09-27 14:25

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0011_checkin_total_harga'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tanggal_check_out', models.DateTimeField(default=django.utils.timezone.now)),
                ('total_harga', models.DecimalField(decimal_places=2, max_digits=10)),
                ('check_in', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotel.checkin')),
            ],
        ),
    ]
