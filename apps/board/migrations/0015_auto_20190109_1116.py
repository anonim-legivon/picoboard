# Generated by Django 2.1.5 on 2019-01-09 01:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0014_auto_20190108_1640'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='is_deleted',
        ),
        migrations.AddField(
            model_name='post',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='thread',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
