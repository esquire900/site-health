# Generated by Django 3.0.7 on 2020-06-23 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20200622_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='url',
        ),
        migrations.AddField(
            model_name='page',
            name='url_part',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
    ]
