# Generated by Django 3.0.7 on 2020-06-22 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metric', '0005_auto_20200622_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirectmetrics',
            name='redirect_is_permanent',
            field=models.BooleanField(null=True),
        ),
    ]
