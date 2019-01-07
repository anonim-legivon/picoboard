# Generated by Django 2.1.5 on 2019-01-07 05:06

import django_regex.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0003_auto_20190107_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='filesize_limit',
            field=models.PositiveIntegerField(default=20971520,
                                              verbose_name='лимит на размер файлов'),
        ),
        migrations.AlterField(
            model_name='spamword',
            name='expression',
            field=django_regex.fields.RegexField(
                verbose_name='регулярное выражение'),
        ),
    ]