# Generated by Django 5.0 on 2024-11-04 11:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0022_roomservice'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomservice',
            name='kategori_layanan',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='hotel.kategorilayanan'),
        ),
        migrations.AlterField(
            model_name='room',
            name='status',
            field=models.CharField(choices=[('Tersedia', 'Tersedia'), ('Tidak Tersedia', 'Tidak Tersedia'), ('Dalam Perawatan', 'Dalam Perawatan')], default='Tersedia', max_length=20),
        ),
        migrations.AlterField(
            model_name='roomservice',
            name='deskripsi_layanan',
            field=models.TextField(),
        ),
    ]