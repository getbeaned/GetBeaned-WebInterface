# Generated by Django 2.1.3 on 2018-11-13 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinterface', '0011_guildsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guildsettings',
            name='bot_prefix',
            field=models.CharField(default='+', max_length=15, verbose_name='bot prefix'),
        ),
    ]
