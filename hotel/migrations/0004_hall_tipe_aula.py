# Generated by Django 5.0 on 2024-09-19 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0003_hall_roomtype_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='hall',
            name='tipe_aula',
            field=models.CharField(choices=[('available', 'Tersedia'), ('reserved', 'Dipesan'), ('maintenance', 'Dalam Perawatan')], default='available', max_length=20),
        ),
    ]
