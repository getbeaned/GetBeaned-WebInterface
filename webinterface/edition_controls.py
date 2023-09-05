import django
from django.contrib.auth.models import User

from webinterface import models
from webinterface.models import DiscordUser


def can_edit(who, what):
    if isinstance(who, models.DiscordUser):
        pass
    elif isinstance(who, int) or isinstance(who, str):
        try:
            who = DiscordUser.objects.get(discord_id=int(who))
        except:
            return False
    elif isinstance(who, User):
        try:
            if who.is_staff:
                return True
            who = DiscordUser.objects.get(discord_id=int(who.socialaccount_set.all()[0].uid))
        except:
            return False
    elif hasattr(who, 'is_authenticated'):
        # Anonymous user
        return False
    else:
        raise Exception(f"I don't know what to do with an object of type {type(who)} for 'who' ")

    if isinstance(what, models.Action):
        if who == what.responsible_moderator or \
                who in what.guild.settings.permissions_admins.all() or \
                who == what.guild.owner:
            return True
        else:
            return False
    elif isinstance(what, models.DiscordGuild):
        if who == what.owner or \
                who in what.settings.permissions_admins.all():
            return True
        else:
            return False
    else:
        raise Exception(f"I don't know what to do with an object of type {type(what)} for 'what' ")
