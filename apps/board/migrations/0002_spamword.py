# Generated by Django 2.1.5 on 2019-01-07 03:10

import django_regex.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0001_squashed_0006_auto_20190106_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpamWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('expression', django_regex.fields.RegexField(
                    verbose_name='регулярное выржаение')),
                ('for_all_boards', models.BooleanField(default=False,
                                                       verbose_name='для всех досок')),
                ('created', models.DateTimeField(verbose_name='создано')),
                ('boards',
                 models.ManyToManyField(blank=True, related_name='spam_words',
                                        to='board.Board',
                                        verbose_name='доски')),
            ],
            options={
                'verbose_name': 'спам слово',
                'verbose_name_plural': 'спам слова',
            },
        ),
    ]