# Generated by Django 3.0.7 on 2020-06-29 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0005_auto_20200629_1135"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="site",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="site",
            name="is_redirect_domain",
            field=models.BooleanField(default=False),
        ),
    ]
