# Generated by Django 3.1.3 on 2020-11-29 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('excursions', '0002_auto_20201129_0912'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='excursionpattern',
            options={'ordering': ('weekday', 'begining'), 'verbose_name': 'Расписание экскурсии', 'verbose_name_plural': 'Расписание экскурсий'},
        ),
    ]
