# Generated by Django 2.1.5 on 2019-01-10 12:45

import django.db.models.deletion
from django.db import migrations, models

import apps.board.models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0002_auto_20190110_2021'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('file',
                 models.FileField(upload_to=apps.board.models.resolve_save_path,
                                  verbose_name='файл')),
                ('height', models.IntegerField(blank=True, default=0,
                                               verbose_name='высота')),
                ('width', models.IntegerField(blank=True, default=0,
                                              verbose_name='ширина')),
                ('type', models.PositiveSmallIntegerField(
                    choices=[(0, 'картинка'), (1, 'видео')],
                    verbose_name='тип')),
                ('md5', models.TextField(blank=True, default='',
                                         verbose_name='MD5 хэш')),
                ('post',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   related_name='files', to='board.Post',
                                   verbose_name='пост')),
            ],
            options={
                'verbose_name': 'файл',
                'verbose_name_plural': 'файлы',
            },
        ),
    ]
