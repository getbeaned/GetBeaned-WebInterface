from django.utils import timezone

from webinterface.models import DiscordUser, DiscordGuild


def user_processor(request):
    if request.user.is_authenticated:
        discord_logged_user = DiscordUser.objects.filter(discord_id=request.user.socialaccount_set.first().uid).first()
    else:
        discord_logged_user = None

    return {'discord_logged_user': discord_logged_user, 'dark_themes': ["dark", "cyborg"]}


def event_processor(request):
    n = timezone.now()
    april_fools = n.day = 1 and n.month == 4

    return {'april_fools': april_fools}
