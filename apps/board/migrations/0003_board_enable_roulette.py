# Generated by Django 2.1.5 on 2019-01-12 11:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0002_auto_20190112_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='enable_roulette',
            field=models.BooleanField(default=False,
                                      verbose_name='включены кубики'),
        ),
    ]
