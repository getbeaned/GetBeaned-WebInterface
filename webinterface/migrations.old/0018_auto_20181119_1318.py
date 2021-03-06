# Generated by Django 2.1.3 on 2018-11-19 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinterface', '0017_auto_20181117_1450'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_multiplictor_bot_banned',
            field=models.FloatField(default=0.25, verbose_name='message author is banned from the bot'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_multiplictor_have_nitro',
            field=models.FloatField(default=-0.75, verbose_name='message author have nitro'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_multiplictor_have_roles',
            field=models.FloatField(default=-0.1, verbose_name='message author have more than a role in the server'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_multiplictor_just_joined',
            field=models.FloatField(default=0.5, verbose_name='message author just joined the server (in for less than a day)'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_multiplictor_new_account',
            field=models.FloatField(default=0.75, verbose_name='message author account is new (less than a week old)'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_multiplictor_offline',
            field=models.FloatField(default=0.15, verbose_name='message author is offline'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_bad_words',
            field=models.FloatField(default=0.15, verbose_name='message conatins bad_ words (score added for every bad word)'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_caps',
            field=models.FloatField(default=1, verbose_name='message written in CAPS LOCK'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_contain_invites',
            field=models.FloatField(default=2.5, verbose_name='message contain untrusted invites'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_embed',
            field=models.FloatField(default=5, verbose_name="message contain a rich embed (can't be sent by users without userbots)"),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_everyone',
            field=models.FloatField(default=1, verbose_name='message contain a failed @everyone ping'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_repeated',
            field=models.FloatField(default=0.25, verbose_name='message was repeated more than 3 times (score added for every repeat)'),
        ),
        migrations.AddField(
            model_name='guildsettings',
            name='automod_score_too_many_mentions',
            field=models.FloatField(default=1, verbose_name='message contain too many user mentions (more than 3)'),
        ),
    ]
