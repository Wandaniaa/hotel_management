# Generated by Django 5.0 on 2024-11-06 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0023_roomservice_kategori_layanan_alter_room_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='layanan',
            field=models.ManyToManyField(blank=True, to='hotel.layanan'),
        ),
    ]
