# Generated by Django 3.0.7 on 2020-06-22 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metric', '0002_auto_20200622_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagestatus',
            name='time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='sslexpiration',
            name='time',
            field=models.DateTimeField(),
        ),
    ]