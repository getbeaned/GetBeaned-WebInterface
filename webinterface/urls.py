from django.urls import path
from django.conf.urls import url
from django.urls import (path, include)

from . import views




urlpatterns = [
    path('',    views.web_index, name='web-index'),
    path('stats',    views.web_stats, name='web-stats'),
    path('sinfo', views.session_info, name='session-info'),

    path('api', views.api_index, name='api-index'),

    # Guilds

    path('guilds',                views.web_guild_list,    name='web-guilds-list'),
    path('guilds/<int:guild_id>', views.web_guild_details, name='web-guild-details'),
    path('guilds/<int:guild_id>/edit', views.web_guild_edit_details, name='web-guild-edit-details'),

    path('api/guilds/', views.api_guilds, name='api-guilds'),

    # Users

    path('users',               views.web_user_list,    name='web-users-list'),
    path('users/<int:user_id>', views.web_user_details, name='web-user-details'),
    path('users/<int:guild_id>/<int:user_id>', views.web_user_details, name='web-user-details'),

    path('api/users/', views.api_users, name='api-users'),
    path('api/users/<int:guild_id>/<int:user_id>/counters/', views.api_users_counters, name='api-users-counters'),

    # Actions

    path('actions',                 views.web_action_list,    name='web-actions-list'),
    path('actions/<int:action_id>', views.web_action_details, name='web-action-details'),
    path('actions/<int:action_id>/edit', views.web_action_edit_details, name='web-action-edit-details'),

    path('api/actions/', views.api_actions, name='api-actions'),
    path('api/settings/<int:guild_id>/', views.api_settings, name='api-settings'),
    path('api/settings/<int:guild_id>/add_staff/', views.api_add_position, name='api-add-positon'),

    path('api/tasks/', views.api_tasks, name="api-get-tasks"),
    path('api/tasks/<int:task_id>/complete', views.api_complete_task, name="api-complete-tasks"),

    path('api/rolepersist/<int:guild_id>/<int:user_id>', views.api_rolepersist, name="api-rolepersist"),

]