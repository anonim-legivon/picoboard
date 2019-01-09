# Generated by Django 2.1.5 on 2019-01-09 01:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0016_auto_20190109_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='posts', to='board.Thread',
                                    verbose_name='тред'),
        ),
    ]
