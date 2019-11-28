import json
import datetime
import re

import django.utils.html
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone

from django.views.decorators.cache import cache_page
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.vary import vary_on_cookie

from collections import defaultdict
from django.db.models.functions import ExtractHour

from webinterface.edition_controls import can_edit
from webinterface.forms import DiscordUserForm, DiscordGuildForm, ActionForm, ActionEditForm, WebSettingsForm, BotTaskForm
from .models import DiscordUser, DiscordGuild, Action, APIAccess, GuildSettings, ACTIONS_TYPES, BotTask, RolePersist

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

    latest_action = Action.objects.filter(guild___settings__logs_security_level="1").latest(field_name="id")

    # latest_actions = Action.objects.order_by('-id')[:4]
    latest_actions = [latest_action, Action.objects.get(id=1319), Action.objects.get(id=1286), Action.objects.get(id=1143)]

    return render(request, 'public/index.html', {"stats": stats, "latest_actions": latest_actions})


def session_info(request):
    return JsonResponse({
        "user": request.user.username,
        "accounts": len(request.user.socialaccount_set.all()),
        "discord_id": request.user.socialaccount_set.first().uid,
        "logged_in": DiscordUser.objects.filter(discord_id=request.user.socialaccount_set.first().uid).first().discord_name,
    })


@cache_page(60 * 1)
@vary_on_cookie
def web_stats(request):
    COLORS = {
        'unban': 'green',
        'unmute': 'darkgreen',
        'note': 'grey',
        'warn': 'orange',
        'mute': 'rebeccapurple',
        'kick': 'orangered',
        'softban': 'red',
        'ban': 'darkred',
    }
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
    actions = Action.objects.select_related('responsible_moderator').only('action_type', 'responsible_moderator__discord_id').annotate(
        hour=ExtractHour('timestamp')).order_by().all()

    # create a default dict to insert a list if key is not exist
    graph_actions_time_y = list(range(0, 24))

    graph_actions_time_x = defaultdict(lambda: [0] * 24)
    graph_actions_time_am_x = defaultdict(lambda: [0] * 24)

    graph_actions = defaultdict(int)

    for row in actions:
        if int(row.responsible_moderator.discord_id) > 999:
            graph_actions_time_x[row.action_type][row.hour] += 1
            graph_actions[row.action_type] += 1

        elif int(row.responsible_moderator.discord_id) == 1:
            graph_actions_time_am_x[row.action_type][row.hour] += 1

    graph_actions = json.dumps([{"name": key, "y": value, "color": COLORS[key]} for key, value in graph_actions.items()])

    guilds = DiscordGuild.objects.select_related('_settings').only('discord_id', 'discord_name', 'discord_user_count', '_settings__automod_enable', '_settings__autoinspect_enable',
                                                                   'last_modified').filter(
        discord_user_count__gt=15).annotate(actions_count=Count('actions')).all()

    graph_servers_member_count_data = {"automod": [], "notautomod": [], "removed": []}

    graph_servers_member_vs_actions_data = {"automod": [], "notautomod": [], "removed": []}
    for g in guilds:
        # graph_servers_member_count_data
        p = {'name': django.utils.html.escape(g.discord_name), 'value': g.discord_user_count, 'guild_id': str(g.discord_id)}
        p2 = {'name': django.utils.html.escape(g.discord_name), 'x': g.discord_user_count, 'y': g.actions_count, 'guild_id': str(g.discord_id)}
        if g.last_modified < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7):
            graph_servers_member_count_data["removed"].append(p)
            graph_servers_member_vs_actions_data["removed"].append(p2)
        elif g.settings.automod_enable or g.settings.autoinspect_enable:
            graph_servers_member_count_data["automod"].append(p)
            graph_servers_member_vs_actions_data["automod"].append(p2)
        else:
            graph_servers_member_count_data["notautomod"].append(p)
            graph_servers_member_vs_actions_data["notautomod"].append(p2)

    graph_servers_member_count_data["automod"] = json.dumps(graph_servers_member_count_data["automod"])
    graph_servers_member_count_data["notautomod"] = json.dumps(graph_servers_member_count_data["notautomod"])
    graph_servers_member_count_data["removed"] = json.dumps(graph_servers_member_count_data["removed"])

    graph_servers_member_vs_actions_data["automod"] = json.dumps(graph_servers_member_vs_actions_data["automod"])
    graph_servers_member_vs_actions_data["notautomod"] = json.dumps(graph_servers_member_vs_actions_data["notautomod"])
    graph_servers_member_vs_actions_data["removed"] = json.dumps(graph_servers_member_vs_actions_data["removed"])

    return render(request, 'public/stats.html', {"general_stats": general_stats,
                                                 "graph_moderators_data": graph_moderators_data,
                                                 "graph_actions": graph_actions,
                                                 "graph_actions_time_y": graph_actions_time_y,
                                                 "graph_actions_time_x": graph_actions_time_x,
                                                 "graph_actions_time_am_x": graph_actions_time_am_x,
                                                 "graph_servers_member_count_data": graph_servers_member_count_data,
                                                 "graph_servers_member_vs_actions_data": graph_servers_member_vs_actions_data})


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


def can_access_actions(guild, logged_in_user=None, return_list=False, specific_action:Action=None):
    logs_security_level = int(guild.settings.logs_security_level)
    if logs_security_level in [1, 2]:
        if return_list:
            return guild.actions.all()
        else:
            return True
    elif logs_security_level in [3, 4]:
        logged_user = logged_in_user

        if not logged_user:
            if return_list:
                return Action.objects.none()
            else:
                return False
        else:
            logged_user_id = logged_user.discord_id

            if logged_user_id in [138751484517941259]:
                if return_list:
                    return guild.actions.all()
                else:
                    return True

            if logs_security_level == 3 and \
                    (guild.settings.permissions_trusted.filter(discord_id=logged_user_id).exists() or
                     guild.settings.permissions_moderators.filter(discord_id=logged_user_id).exists() or
                     guild.settings.permissions_admins.filter(discord_id=logged_user_id).exists() or
                     logged_user_id == guild.owner_id
                    ):
                if return_list:
                    return guild.actions.all()
                else:
                    return True

            elif logs_security_level == 4 and \
                    (guild.settings.permissions_admins.filter(discord_id=logged_user_id).exists() or
                     logged_user_id == guild.owner_id):
                if return_list:
                    return guild.actions.all()
                else:
                    return True

            else:
                if return_list:
                    return guild.actions.filter(responsible_moderator__discord_id=logged_user_id) | \
                           guild.actions.filter(user__discord_id=logged_user_id)
                else:
                    if specific_action:
                        return specific_action.responsible_moderator.discord_id == logged_user_id or \
                                specific_action.user.discord_id == logged_user_id
                    return False


@vary_on_cookie
def web_guild_details(request, guild_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)
    if request.user.is_authenticated:
        logged_user = DiscordUser.objects.filter(discord_id=request.user.socialaccount_set.first().uid).first()
    else:
        logged_user = None

    actions_list = can_access_actions(guild, logged_in_user=logged_user, return_list=True)

    page = request.GET.get('page')
    actions = Paginator(actions_list, 8).get_page(page)

    return render(request, 'public/guild-details.html', {'guild': guild, 'actions': actions})


@login_required()
def web_guild_edit_details(request, guild_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)

    if not can_edit(request.user, guild):
        raise PermissionDenied

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


def web_user_pfp(request, user_id: int):
    user = get_object_or_404(DiscordUser, discord_id=user_id)
    user.refresh_from_bot()

    return HttpResponseRedirect(user.discord_default_avatar_url)


@vary_on_cookie
def web_user_details(request, user_id: int, guild_id=None):
    user = get_object_or_404(DiscordUser, discord_id=user_id)

    if request.user.is_authenticated:
        logged_user_id = request.user.socialaccount_set.first().uid
    else:
        logged_user_id = None

    if guild_id:
        guild = get_object_or_404(DiscordGuild, discord_id=guild_id)
        actions_received = user.actions_received.filter(guild_id=guild_id).all()
        actions_given = user.actions_given.filter(guild_id=guild_id).all()
    else:
        actions_received = user.actions_received.all()
        actions_given = user.actions_given.all()
        guild = None

    restrict_query = Q(guild___settings__logs_security_level=1) | Q(guild___settings__logs_security_level=2)

    if logged_user_id:
        restrict_query = restrict_query | Q(responsible_moderator__discord_id=logged_user_id) | Q(user__discord_id=logged_user_id)

    actions_received = actions_received.filter(restrict_query)
    actions_given = actions_given.filter(restrict_query)

    par = Paginator(actions_received, 4)
    pag = Paginator(actions_given, 4)

    return render(request, 'public/user-details.html',
                  {'d_user': user, 'guild': guild, 'actions_received': par.get_page(request.GET.get('page_ar')),
                   'actions_given': pag.get_page(request.GET.get('page_ag')), 'par': par.count, 'pag': pag.count})


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
        actions = Action.objects.filter(user=user, guild=guild, pardonned=False).all()
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

    if request.user.is_authenticated:
        logged_user = DiscordUser.objects.filter(discord_id=request.user.socialaccount_set.first().uid).first()
    else:
        logged_user = None

    access_granted = can_access_actions(action.guild, logged_in_user=logged_user, return_list=True, specific_action=action)
    if access_granted:
        return render(request, 'public/action-details.html', {'action': action})
    else:
        raise PermissionDenied


@login_required()
def web_action_edit_details(request, action_id: int):
    action = get_object_or_404(Action, id=action_id)
    if not can_edit(request.user, action):
        raise PermissionDenied

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


@api_login_required
@csrf_exempt
def api_tasks(request):

    if request.method == 'POST':
        form = BotTaskForm(request.POST)

        if form.is_valid():
            task = form.save()
            return JsonResponse({'status': 'ok', 'message': 'Task created with success', 'result': str(task)})

        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        tasks = BotTask.objects.filter(completed=False).filter(execute_at__lt=timezone.now()).all()

        task_list = []

        for task in tasks:
            task_list.append({
                "id": task.id,
                "type": task.task_type,
                "arguments": task.arguments
            })

        return JsonResponse(task_list, safe=False)


@api_login_required
@csrf_exempt
def api_rolepersist(request, guild_id: int, user_id: int):
    guild = get_object_or_404(DiscordGuild, discord_id=guild_id)
    user = get_object_or_404(DiscordUser, discord_id=user_id)

    if request.method == 'POST':
        role_persist, created = RolePersist.objects.update_or_create(
            guild=guild, user=user,
            defaults={'roles_ids': request.POST.get("roles_ids", "")},
        )
        return JsonResponse({'status': 'ok', 'message': 'Roles stored with success', 'result': str(role_persist), 'created': created})
    else:
        default_roles = guild.settings.rolepersist_default_roles
        try:
            role_persist = RolePersist.objects.get(guild=guild, user=user).roles_ids
            role_persist = ",".join(set(role_persist.split(",") + re.split("; \n,", default_roles)))
        except RolePersist.DoesNotExist:
            role_persist = ",".join(set(re.split("; \n,", default_roles)))

        return JsonResponse({'status': 'ok', 'roles': role_persist})


@api_login_required
@csrf_exempt
def api_complete_task(request, task_id):
    task = get_object_or_404(BotTask, id=task_id)

    task.completed = True
    task.save()

    return JsonResponse({"ok": True})
