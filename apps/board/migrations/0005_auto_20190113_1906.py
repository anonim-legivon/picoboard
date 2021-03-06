# Generated by Django 2.1.5 on 2019-01-13 09:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('board', '0004_board_image_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='duration',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              verbose_name='длительность'),
        ),
        migrations.AddField(
            model_name='file',
            name='thumbnail',
            field=models.ImageField(blank=True, height_field='tn_height',
                                    upload_to='', verbose_name='thumbnail',
                                    width_field='tn_width'),
        ),
        migrations.AddField(
            model_name='file',
            name='tn_height',
            field=models.IntegerField(blank=True, default=0,
                                      verbose_name='высота thumbnail'),
        ),
        migrations.AddField(
            model_name='file',
            name='tn_width',
            field=models.IntegerField(blank=True, default=0,
                                      verbose_name='ширина thumbnail'),
        ),
    ]
