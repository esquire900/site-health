# Generated by Django 3.0.7 on 2020-06-22 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20200622_1432'),
        ('metric', '0004_pagecontentlength'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeaderMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('status_code', models.SmallIntegerField()),
                ('content_length', models.IntegerField(null=True)),
                ('sec_since_last_modified', models.IntegerField(null=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RedirectMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('num_redirects', models.SmallIntegerField()),
                ('redirect_is_permanent', models.BooleanField()),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='pagestatus',
            name='page',
        ),
        migrations.DeleteModel(
            name='PageContentLength',
        ),
        migrations.DeleteModel(
            name='PageStatus',
        ),
    ]
