# Generated by Django 2.1.5 on 2019-01-08 05:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0010_board_trip_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='name_allowed',
            field=models.BooleanField(default=False,
                                      verbose_name='разрешены имена'),
        ),
    ]