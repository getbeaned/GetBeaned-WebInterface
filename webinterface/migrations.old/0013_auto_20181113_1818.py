# Generated by Django 2.1.3 on 2018-11-13 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinterface', '0012_auto_20181113_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guildsettings',
            name='permissions_admins',
            field=models.ManyToManyField(blank=True, null=True, related_name='admin_status', to='webinterface.DiscordUser', verbose_name='additional admins'),
        ),
        migrations.AlterField(
            model_name='guildsettings',
            name='permissions_banned',
            field=models.ManyToManyField(blank=True, null=True, related_name='banned_status', to='webinterface.DiscordUser', verbose_name='additional banned users'),
        ),
        migrations.AlterField(
            model_name='guildsettings',
            name='permissions_moderators',
            field=models.ManyToManyField(blank=True, null=True, related_name='moderator_status', to='webinterface.DiscordUser', verbose_name='additional moderators'),
        ),
        migrations.AlterField(
            model_name='guildsettings',
            name='permissions_trusted',
            field=models.ManyToManyField(blank=True, null=True, related_name='trusted_status', to='webinterface.DiscordUser', verbose_name='additional trusted users'),
        ),
    ]
