# Generated by Django 2.1.3 on 2019-01-16 21:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webinterface', '0002_auto_20190113_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guildsettings',
            old_name='tresholds_enable',
            new_name='thresholds_enable',
        ),
        migrations.RenameField(
            model_name='guildsettings',
            old_name='tresholds_kicks_to_bans',
            new_name='thresholds_kicks_to_bans',
        ),
        migrations.RenameField(
            model_name='guildsettings',
            old_name='tresholds_softbans_to_bans',
            new_name='thresholds_softbans_to_bans',
        ),
        migrations.RenameField(
            model_name='guildsettings',
            old_name='tresholds_warns_to_kick',
            new_name='thresholds_warns_to_kick',
        ),
    ]