# Generated by Django 2.1.3 on 2018-11-20 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webinterface', '0024_guildsettings_imported_bans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guildsettings',
            name='guild',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='_settings', to='webinterface.DiscordGuild'),
        ),
        migrations.AlterField(
            model_name='guildsettings',
            name='imported_bans',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='guildsettings',
            name='tresholds_enable',
            field=models.BooleanField(default=False, verbose_name='enable thresholds'),
        ),
    ]
