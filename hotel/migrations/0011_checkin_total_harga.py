# Generated by Django 5.0 on 2024-09-21 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0010_rename_hall_checkin_aula_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='total_harga',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
