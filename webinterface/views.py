import json

import django.utils.html
from django.core.paginator import Paginator

from django.views.decorators.cache import cache_page
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_cookie

from collections import defaultdict
from django.db.models.functions import ExtractHour

from webinterface.edition_controls import can_edit
from webinterface.forms import DiscordUserForm, DiscordGuildForm, ActionForm, ActionEditForm, WebSettingsForm
from .models import DiscordUser, DiscordGuild, Action, APIAccess, GuildSettings, ACTIONS_TYPES

from functools import wraps
from django.http import HttpResponseRedirect
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def api_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):

        token = request.META.get('http_authorization'.upper(), None)
        api_access = APIAccess.objects.filter(token=token).first()

        if api_access:
            return function(request, *args, **kwargs)
        else:
            return JsonResponse({'version': 1, 'logged_in': 'error'})

    return wrap


# Create your views here.


# Indexes

@cache_page(60 * 1)
@vary_on_cookie
def web_index(request):
    stats = {
        "actions_count": Action.objects.count(),
        "guilds_count": DiscordGuild.objects.count(),
        "users_count": DiscordUser.objects.count(),
        "automod_enabled_count": GuildSettings.objects.filter(automod_enable=True).count(),
        "autotrigger_enabled_count": GuildSettings.objects.filter(autotrigger_enable=True).count(),
        "thresholds_enabled_count": GuildSettings.objects.filter(thresholds_enable=True).count(),
    }

    # latest_actions = Action.objects.order_by('-id')[:4]
    latest_actions = [Action.objects.latest(field_name="id"), Action.objects.get(id=1319), Action.objects.get(id=1286), Action.objects.get(id=1143)]

    return render(request, 'public/index.html', {"stats": stats, "latest_actions": latest_actions})


@cache_page(60 * 1)
@vary_on_cookie
def web_stats(request):
    general_stats = {
        "actions_count": Action.objects.count(),
        "guilds_count": DiscordGuild.objects.count(),
        "users_count": DiscordUser.objects.count(),
        "automod_enabled_count": GuildSettings.objects.filter(automod_enable=True).count(),
        "autotrigger_enabled_count": GuildSettings.objects.filter(autotrigger_enable=True).count(),
        "thresholds_enabled_count": GuildSettings.objects.filter(thresholds_enable=True).count(),
    }

    automod = Action.objects.filter(responsible_moderator__discord_id__exact=1).count()
    normalmod = Action.objects.filter(responsible_moderator__discord_id__gt=999).count()

    graph_moderators_data = json.dumps(
        [
            {"name": "AutoModerator", "y": automod},
            {"name": "Human Moderators", "y": normalmod}
        ]
    )

    # create a new field to extract hour from timestamp field
    actions = Action.objects.select_related('responsible_moderator').only('action_type', 'responsible_moderator__discord_id').annotate(hour=ExtractHour('timestamp')).order_by().all()

    # create a default dict to insert a list if key is not exist
    graph_actions_time_y = list(range(0, 24))

    graph_actions_time_x = defaultdict(lambda: [0] * 24)
    graph_actions_time_am_x = defaultdict(lambda: [0] * 24)

    for row in actions:
        if int(row.responsible_moderator.discord_id) > 999:
            graph_actions_time_x[row.action_type][row.hour] += 1
        elif int(row.responsible_moderator.discord_id) == 1:
            graph_actions_time_am_x[row.action_type][row.hour] += 1

    guilds = DiscordGuild.objects.select_related('_settings').only('discord_id', 'discord_name', 'discord_user_count', '_settings__automod_enable').filter(discord_user_count__gt=15).all()

    graph_servers_member_count_data = {"automod": [], "notautomod": []}

    for g in guilds:
        p = {'name': django.utils.html.escape(g.discord_name), 'value': g.discord_user_count, 'guild_id': str(g.discord_id)}
        if g.settings.automod_enable:
            graph_servers_member_count_data["automod"].append(p)
        else:
            graph_servers_member_count_data["notautomod"].append(p)

    graph_servers_member_count_data["automod"] = json.dumps(graph_servers_member_count_data["automod"])
    graph_servers_member_count_data["notautomod"] = json.dumps(graph_servers_member_count_data["notautomod"])

    return render(request, 'public/stats.html', {"general_stats": general_stats,
                                                 "graph_moderators_data": graph_moderators_data,
                                                 "graph_actions_time_y": graph_actions_time_y,
                                                 "graph_actions_time_x": graph_actions_time_x,
                                                 "graph_actions_time_am_x": graph_actions_time_am_x,
                                                 "graph_servers_member_count_data": graph_servers_member_count_data})


@api_login_required
@csrf_exempt
def api_index(request):
    token = request.META.get('http_Authorization', None)
    api_access = APIAccess.objects.filter(token=token).first()

    if api_access:
        return JsonResponse({'version': 1, 'logged_in': 'ok'})
    else:
        return JsonResponse({'version': 1, 'logged_in': 'error'})


# Guilds
@vary_on_cookie
def web_guild_list(request):
    return render(request, 'public/index.html')


@vary_on_cookie
def web_guild_details(request, guild_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)
    actions_list = guild.actions.all()
    page = request.GET.get('page')
    actions = Paginator(actions_list, 8).get_page(page)

    return render(request, 'public/guild-details.html', {'guild': guild, 'actions': actions})


@login_required()
def web_guild_edit_details(request, guild_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)

    if not can_edit(request.user, guild):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = WebSettingsForm(request.POST, instance=guild.settings)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('web-guild-details', kwargs={"guild_id": guild_id}))
    else:
        form = WebSettingsForm(instance=guild.settings)

    form.fields["permissions_admins"].queryset = guild.settings.permissions_admins.all()
    form.fields["permissions_moderators"].queryset = guild.settings.permissions_moderators.all()
    form.fields["permissions_trusted"].queryset = guild.settings.permissions_trusted.all()
    form.fields["permissions_banned"].queryset = guild.settings.permissions_banned.all()
    # logger.warn(json.dumps(form.errors))
    return render(request, 'public/guild-edit-details.html', {'guild': guild, 'form': form})


@api_login_required
@csrf_exempt
def api_guilds(request):
    if request.method == 'POST':
        form = DiscordGuildForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user, created = DiscordGuild.objects.update_or_create(discord_id=data['discord_id'], defaults=data)

            if created:
                return JsonResponse({'status': 'ok', 'message': 'Guild created with success', 'result': str(user)})
            else:
                return JsonResponse({'status': 'ok', 'message': 'Guild updated with success', 'result': str(user)})

        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        return JsonResponse({'status': 'Not Implemented'})


@api_login_required
@csrf_exempt
def api_settings(request, guild_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)

    if request.method == 'POST':
        try:
            settings = guild.settings
            setattr(settings, request.POST.get('setting'), request.POST.get('value'))
            settings.save()

            settings = guild.settings

            data = serializers.serialize('json', [settings, ])
            struct = json.loads(data)[0]['fields']

            return JsonResponse({'status': 'ok', 'result': struct})
        except Exception as e:
            logger.exception(f"In api_settings (POST) : {type(e).__name__} : {e}")
            return JsonResponse({'status': 'error', 'error_message': f"{type(e).__name__} : {e}"})
    else:
        settings = guild.settings

        data = serializers.serialize('json', [settings, ])
        struct = json.loads(data)[0]['fields']

        return JsonResponse(struct)


@api_login_required
@csrf_exempt
def api_add_position(request, guild_id: int):
    if request.method == 'POST':
        position = request.POST.get('position')
        user_id = request.POST.get('user')

        user = get_object_or_404(DiscordUser, discord_id=user_id)
        guild = get_object_or_404(DiscordGuild, discord_id=guild_id)

        if position == 'banned':
            guild.settings.permissions_banned.add(user)
        elif position == 'trusted':
            guild.settings.permissions_trusted.add(user)
        elif position == 'moderators':
            guild.settings.permissions_moderators.add(user)
        elif position == 'admins':
            guild.settings.permissions_admins.add(user)

        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'Not Implemented'})


# Users

@vary_on_cookie
def web_user_list(request):
    return render(request, 'public/index.html')


@vary_on_cookie
def web_user_details(request, user_id: int, guild_id=None):
    user = get_object_or_404(DiscordUser, discord_id=user_id)

    if guild_id:
        guild = get_object_or_404(DiscordGuild, discord_id=guild_id)
        actions_received = user.actions_received.filter(guild_id=guild_id).all()
        actions_given = user.actions_given.filter(guild_id=guild_id).all()
    else:
        actions_received = user.actions_received.all()
        actions_given = user.actions_given.all()
        guild = None

    return render(request, 'public/user-details.html',
                  {'d_user': user, 'guild': guild, 'actions_received': Paginator(actions_received, 4).get_page(request.GET.get('page_ar')),
                   'actions_given': Paginator(actions_given, 4).get_page(request.GET.get('page_ag'))})


@api_login_required
@csrf_exempt
def api_users(request):
    if request.method == 'POST':

        form = DiscordUserForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            should_update = request.META.get('http_update'.upper(), True)

            if should_update:
                user, created = DiscordUser.objects.update_or_create(discord_id=data['discord_id'], defaults=data)
            else:
                user, created = DiscordUser.objects.get_or_create(discord_id=data['discord_id'], defaults=data)

            if created:
                return JsonResponse({'status': 'ok', 'message': 'User created with success', 'result': str(user)})
            elif should_update:
                return JsonResponse({'status': 'ok', 'message': 'User updated with success', 'result': str(user)})
            else:
                return JsonResponse(
                    {'status': 'ok', 'message': 'User existed in database already', 'result': str(user)})

        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        return JsonResponse({'status': 'Not Implemented'})


@api_login_required
@csrf_exempt
def api_users_counters(request, guild_id: int, user_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)
    user = get_object_or_404(DiscordUser, discord_id=user_id)

    if request.method == 'POST':
        return JsonResponse({'status': 'Not Implemented'})
    else:
        counters = {key[0]: 0 for key in ACTIONS_TYPES}
        actions = Action.objects.filter(user=user, guild=guild).all()
        for action in actions:
            counters[action.action_type] += 1

        return JsonResponse(counters)


# Actions

@vary_on_cookie
def web_action_list(request):
    return render(request, 'public/index.html')


@vary_on_cookie
def web_action_details(request, action_id: int):
    action = get_object_or_404(Action, id=action_id)
    return render(request, 'public/action-details.html', {'action': action})


@login_required()
def web_action_edit_details(request, action_id: int):
    action = get_object_or_404(Action, id=action_id)
    if not can_edit(request.user, action):
        return HttpResponseForbidden()

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ActionEditForm(request.POST, instance=action)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('web-action-details', kwargs={'action_id': action_id}))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ActionEditForm(instance=action)

    return render(request, 'public/action-details-edit.html', {'action': action, 'form': form})


@api_login_required
@csrf_exempt
def api_actions(request):
    if request.method == 'POST':

        form = ActionForm(request.POST)

        if form.is_valid():
            action = form.save()

            return JsonResponse({'status': 'ok', 'message': 'Action created with success', 'result': str(action),
                                 'result_url': reverse('web-action-details', kwargs={'action_id': action.id}),
                                 'case_number': str(action.id)})

        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        return JsonResponse({'status': 'Not Implemented'})
