# Generated by Django 2.1.5 on 2019-01-08 05:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0011_board_name_allowed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='name_allowed',
            new_name='enable_names',
        ),
    ]