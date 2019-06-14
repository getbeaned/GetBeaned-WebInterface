import collections
import re
import uuid

from django.conf import settings

from django.db import models
from django.urls import reverse
from django.utils import timezone

from django.utils.html import escape, mark_safe

from math import log

ACTIONS_TYPES = (
    ('ban', 'Ban'),
    ('unban', 'Unban'),
    ('softban', 'Softban'),
    ('kick', 'Kick'),
    ('warn', 'Warn'),
    ('note', 'Note'),
    ('mute', 'Mute'),
    ('unmute', 'Unmute'),
)


# Create your models here.

class DiscordUser(models.Model):
    discord_id = models.CharField(max_length=40, primary_key=True, unique=True)
    discord_name = models.CharField(max_length=200)
    discord_discriminator = models.IntegerField()
    discord_avatar_url = models.URLField()
    discord_default_avatar_url = models.URLField()
    discord_bot = models.BooleanField()

    admin_info = models.TextField(default=None, null=True, blank=True)

    @property
    def admin_url(self):
        return reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.pk,))

    @property
    def discord_discriminator_str(self):
        return str(self.discord_discriminator).zfill(4)

    @property
    def settings(self):
        try:
            return self._settings
        except UserSettings.DoesNotExist:
            return UserSettings.objects.create(
                user=self,
            )

    @property
    def security_score(self):
        """
        An index of the dangerosity of an user
        :return:
        """

        def member_count_softener(x):
            """
            This function will take the member count of a server and dampen it to fit on a way smaller scale, but a non-linear one

            https://www.wolframalpha.com/input/?i=plot+(log(x%2Flog(x))+-+4.5)+from+100+to+100000
            """
            return max(0., log(x / log(x)) - 4.5)

        actions = self.actions_received.order_by("id").all()
        action_mapping = {
            "softban": 5,
            "kick": 3,
            "mute": 2,
            "warn": 1,
            None: 0
        }

        banned_in = set()
        worst_type = {}

        for action in actions:
            if action.action_type not in ["note", "unmute"] and action.guild.discord_user_count >= 100:
                if action.action_type == "ban":
                    banned_in.add(action.guild)
                elif action.action_type == "unban":
                    try:
                        banned_in.remove(action.guild)
                    except KeyError:
                        pass

                else:
                    cwt = worst_type.get(action.guild)
                    if action_mapping[cwt] <= action_mapping[action.action_type]:
                        worst_type[action.guild] = action.action_type

        bans_index = sum([member_count_softener(g.discord_user_count) * 15 for g in banned_in])
        actions_index = sum([member_count_softener(g.discord_user_count) * action_mapping[worst_type] for g, worst_type in worst_type.items()])

        index = round(bans_index + actions_index, 2)

        return index

    def __str__(self):
        return f"{self.discord_name}#{self.discord_discriminator_str} ({self.discord_id})"


class UserSettings(models.Model):
    user = models.OneToOneField(DiscordUser, on_delete=models.CASCADE, related_name='_settings', db_index=True)

    test_beta_features = models.BooleanField(default=False)
    theme = models.CharField(max_length=40, default="light.css", choices=(("light", "Light Theme"), ("dark", "Dark Theme"), ("cyborg", "Cyborg"), ("lux", "Lux")))


class DiscordGuild(models.Model):
    discord_id = models.CharField(max_length=40, primary_key=True, unique=True)
    discord_name = models.CharField(max_length=200)
    discord_icon_url = models.URLField()
    discord_created_at = models.DateTimeField()
    discord_user_count = models.IntegerField()

    owner = models.ForeignKey(DiscordUser, on_delete=models.DO_NOTHING, related_name='guilds_owned')

    @property
    def admin_url(self):
        return reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.pk,))

    @property
    def settings(self):
        try:
            return self._settings
        except GuildSettings.DoesNotExist:
            return GuildSettings.objects.create(
                guild=self,
            )

    def __str__(self):
        return f"{self.discord_name} ({self.discord_id})"


class GuildSettings(models.Model):
    @property
    def admin_url(self):
        return reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.pk,))

    guild = models.OneToOneField(DiscordGuild, on_delete=models.CASCADE, related_name='_settings', db_index=True)
    imported_bans = models.BooleanField(default=False)

    # AutoInspect
    autoinspect_enable = models.BooleanField(verbose_name="enable AutoInspect", help_text="AutoInspect tries to detect bot accounts when they join.", default=False)

    AUTOINSPECT_ACTIONS = ((1, 'Do Nothing'),
                           (2, 'Warn admins'),
                           (3, 'Kick (use with caution)'),
                           (4, 'Ban (use with caution)'))

    autoinspect_pornspam_bots = models.IntegerField(choices=AUTOINSPECT_ACTIONS, help_text="Bots that come to spam porn on channels.", default=1)


    # AutoTrigger
    autotrigger_enable = models.BooleanField(verbose_name="enable AutoTriggers", default=False)

    autotrigger_sexdatingdiscordbots_score = models.FloatField(
        verbose_name="message looks like a link spam for a \"Sex Dating\" scam website ",
        help_text="Set to 0 to disable",
        default=10
    )

    autotrigger_instantessaydiscordbots_score = models.FloatField(
        verbose_name="message from userbots spamming for an essay writing website",
        help_text="Set to 0 to disable",
        default=10
    )

    autotrigger_sexbots_score = models.FloatField(
        verbose_name="various userbots posting links to porn websites",
        help_text="Set to 0 to disable",
        default=10
    )

    # Automod
    ## Actions
    automod_enable = models.BooleanField(verbose_name="enable Automod", default=False)
    automod_delete_message_score = models.FloatField(
        verbose_name="automod score to delete messages",
        help_text="Set to 0 to disable",
        default=1.5)
    automod_warn_score = models.FloatField(
        verbose_name="automod score to warn the author of a message",
        help_text="Set to 0 to disable",
        default=2)
    automod_kick_score = models.FloatField(
        verbose_name="automod score to kick the author of a message",
        help_text="Set to 0 to disable",
        default=0)
    automod_softban_score = models.FloatField(
        verbose_name="automod score to softban the author of a message",
        help_text="Set to 0 to disable",
        default=7)
    automod_ban_score = models.FloatField(
        verbose_name="automod score to ban the author of a message",
        help_text="Set to 0 to disable",
        default=10)

    ## Multiplicator
    automod_multiplictor_offline = models.FloatField(
        verbose_name="message author is offline",
        help_text="Most spammers use(d) invisible mode to be harder to mention when banning",
        default=0.15
    )

    automod_multiplictor_new_account = models.FloatField(
        verbose_name="message author account is new",
        help_text="Account less than a week old",
        default=0.75
    )

    automod_multiplictor_just_joined = models.FloatField(
        verbose_name="message author just joined the server",
        help_text="Was in the server for less than a day since the last join",
        default=0.5
    )

    automod_multiplictor_have_nitro = models.FloatField(
        verbose_name="message author has nitro",
        help_text="Due to discord limitations, only nitro users with animated avatars are currently detected.",
        default=-0.75
    )

    automod_multiplictor_have_roles = models.FloatField(
        verbose_name="message author have more than one role in the server",
        default=-0.10
    )

    automod_multiplictor_bot_banned = models.FloatField(
        verbose_name="message author is banned from the bot",
        help_text="You can bot-ban people with +add_banned [user] in your server",
        default=0.25
    )

    automod_score_caps = models.FloatField(
        verbose_name="message written in CAPS LOCK",
        help_text="To prevent messages like \"OK\" to be flagged as full-caps, "
                  "messages must be at least 16 chars in length, and shoudn't look like a command (experimental)",
        default=1
    )

    automod_score_embed = models.FloatField(
        verbose_name="message contain a rich embed",
        help_text="Rich embeds cannot be sent by users without using a userbot. "
                  "They are often used to circumvent the message filtering",
        default=5
    )

    automod_score_everyone = models.FloatField(
        verbose_name="message contain a failed @everyone ping",
        help_text="Note that this will only be true if the @everyone ping failed",
        default=1
    )

    automod_score_too_many_mentions = models.FloatField(
        verbose_name="message contain too many user mentions",
        help_text="More than 3 of them",
        default=1
    )

    automod_score_contain_invites = models.FloatField(
        verbose_name="message contain untrusted invites",
        help_text="Untrusted invites are invites for another server that the one they are in, "
                  "with a member count smaller than what's specified in the misc options of the automod",
        default=2.5
    )

    automod_score_repeated = models.FloatField(
        verbose_name="message was repeated more than 3 times",
        help_text="This score is added for every repeat (so, if I sent the same message 4 times, that'd be 4*0.25=1)",
        default=0.25
    )

    automod_score_bad_words = models.FloatField(
        verbose_name="message contains bad words",
        help_text="This score is added for each bad word found in the message. "
                  "Note that this is imperfect and subject to change",
        default=0.15
    )

    automod_score_zalgo = models.FloatField(
        verbose_name="message contains zalgo text",
        help_text="Zalgo is \"corrupted\" text that takes up a lot of screen real-estate and used to crash the discord client.",
        default=1.3
    )

    ## Misc
    automod_ignore_level = models.IntegerField(
        verbose_name="minimum bot level required for automod to ignore you",
        help_text="Level 2 is trusted users, 3 moderators, 4 admins and 5 owner.",
        default=2)

    automod_ignore_invites_in = models.CharField(
        max_length=900,
        verbose_name="channel id where the bot will ignore untrusted invites",
        help_text="Set to 0 to disable ignoring invites in a channel",
        default="0")

    automod_minimal_membercount_trust_server = models.IntegerField(
        verbose_name="Minimum member count to consider a server trusted",
        help_text="Set to 0 to disable trusting servers using their member count",
        default=10000)

    automod_note_message_deletions = models.BooleanField(
        verbose_name="enable adding notes to users when one of their message is deleted by the automod",
        help_text="Notes don't count against thresholds but may clutter up your server display. You can recover a deleted message with +snipe",
        default=False)

    # Dehoister

    dehoist_enable = models.BooleanField(verbose_name="remove special characters from users names (dehoist)",
                                         help_text="Activating this will apply to new nicknames changes only",
                                         default=False)

    dehoist_ignore_level = models.IntegerField(verbose_name="minimum bot level required for the dehoister to ignore you",
                                               help_text="Level 2 is trusted users, 3 moderators, 4 admins and 5 owner.",
                                               default=2
                                               )

    dehoist_intensity = models.CharField(verbose_name="intensity level of the dehoister",
                                         choices=(("1", "Low: only nicknames starying with !"),
                                                  ("2", "Medium: remove all special chars at the beginning of names"),
                                                  ("3", "High: also remove aa from the start of nicknames")),
                                         default=1,
                                         max_length=4
                                         )

    dehoist_action = models.CharField(verbose_name="Action taken when dehoisting a name",
                                      choices=(("nothing", "Dehoist"),
                                               ("message", "Dehoist and inform the user"),
                                               ("note", "Dehoist and add a note to the user"),
                                               ("warn", "Dehoist and warn the user")),
                                      default="note",
                                      max_length=15
                                      )

    # Thresholds

    thresholds_enable = models.BooleanField(verbose_name="enable thresholds", default=False)

    thresholds_warns_to_kick = models.IntegerField(
        verbose_name="number of warns that must be applied to a user before they receive an automatic kick",
        default=3)

    thresholds_mutes_to_kick = models.IntegerField(
        verbose_name="number of mutes that must be applied to a user before they receive an automatic kick",
        default=2)

    thresholds_kicks_to_bans = models.IntegerField(
        verbose_name="number of kicks that must be applied to a user before they receive an automatic ban",
        default=3)

    thresholds_softbans_to_bans = models.IntegerField(
        verbose_name="number of softbans that must be applied to a user before they receive an automatic ban",
        default=2)

    # Permissions
    permissions_admins = models.ManyToManyField(
        to=DiscordUser,
        related_name="admin_status",
        verbose_name="additional admins",
        help_text="Select multiple users with CTRL+click. Add users with +add_admin [user] in your server",
        blank=True
    )

    permissions_moderators = models.ManyToManyField(
        to=DiscordUser,
        related_name="moderator_status",
        verbose_name="additional moderators",
        help_text="Select multiple users with CTRL+click. Add users with +add_moderator [user] in your server",
        blank=True
    )

    permissions_trusted = models.ManyToManyField(
        to=DiscordUser,
        related_name="trusted_status",
        verbose_name="additional trusted users",
        help_text="Select multiple users with CTRL+click. Add users with +add_trusted [user] in your server",
        blank=True,
    )

    permissions_banned = models.ManyToManyField(
        to=DiscordUser,
        related_name="banned_status",
        verbose_name="additional banned users",
        help_text="Select multiple users with CTRL+click. Add users with +add_banned [user] in your server",
        blank=True,
    )

    # Logs

    logs_enable = models.BooleanField(
        verbose_name="enable logging actions to a channel",
        help_text="Set a specific log channel ID to 0 to disable that particular log",
        default=False)

    logs_as_embed = models.BooleanField(verbose_name="use cooler embeds in logs",
                                        help_text="Disable to use plain text",
                                        default=True)

    logs_moderation_channel_id = models.CharField(max_length=40, verbose_name="ID of the channel to log moderation messages to",
                                                  default="0")

    logs_joins_channel_id = models.CharField(max_length=40, verbose_name="ID of the channel to log joins and leaves to",
                                             default="0")
    logs_member_edits_channel_id = models.CharField(max_length=40,
                                                    verbose_name="ID of the channel to log members name changes to", default="0")

    logs_edits_channel_id = models.CharField(max_length=40, verbose_name="ID of the channel to log messages edits to", default="0")
    logs_delete_channel_id = models.CharField(max_length=40, verbose_name="ID of the channel to log messages delete to",
                                              default="0")

    logs_autoinspect_channel_id = models.CharField(max_length=40, verbose_name="ID of the channel to log AutoInspect actions to. This is required if you want AutoInspect to work.",
                                                   default="0")

    # Bot

    bot_prefix = models.CharField(
        max_length=15,
        verbose_name="bot prefix",
        help_text="The g+ prefix will always work, regardless of this setting",
        default="+"
    )

    def __str__(self):
        return f"Settings for guild {self.guild}"


class Action(models.Model):
    @property
    def admin_url(self):
        return reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.pk,))

    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE, related_name='actions', db_index=True)
    user = models.ForeignKey(DiscordUser, on_delete=models.DO_NOTHING, related_name='actions_received', db_index=True)
    action_type = models.CharField(max_length=15, choices=ACTIONS_TYPES)

    reason = models.TextField(max_length=5000, null=True)

    reason_format_regex = re.compile("(?<!&)#(\d+)", re.MULTILINE)

    @property
    def formatted_reason(self):
        reason = re.sub(self.reason_format_regex, lambda m: "<a href=\"" +
                                                            reverse("web-action-details",
                                                                    kwargs={"action_id": m.group(1)}
                                                                    )
                                                            + "\">#" + str(m.group(1)) + "</a>",
                        escape(self.reason))
        return mark_safe(reason)

    automod_logs = models.TextField(null=True, default=None, blank=True)

    attachment = models.URLField(null=True, default=None, blank=True)

    responsible_moderator = models.ForeignKey(DiscordUser, on_delete=models.DO_NOTHING, related_name='actions_given',
                                              null=True, db_index=True)
    timestamp = models.DateTimeField(default=timezone.now)
    until = models.DateTimeField(null=True, default=None, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.action_type} #{self.id} on {self.user}"


def get_token():
    return str(uuid.uuid4().hex)


class APIAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, default=get_token)

    def __str__(self):
        return f"{self.user} access token"
