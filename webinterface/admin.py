from django.contrib import admin
from .models import DiscordUser, DiscordGuild, Action, APIAccess, GuildSettings, UserSettings, BotTask, RolePersist


# Register your models here.

class GuildSettingsInline(admin.TabularInline):
    model = GuildSettings,
    # autocomplete_fields = ['permissions_admins', 'permissions_moderators', 'permissions_trusted', 'permissions_banned']


class GuildAdmin(admin.ModelAdmin):
    model = DiscordGuild,
    readonly_fields = ['_settings']

    list_display = ('discord_name', 'discord_created_at', 'discord_user_count')

    list_filter = ('_settings__automod_enable', '_settings__autotrigger_enable', '_settings__autoinspect_enable')

    autocomplete_fields = ['owner']
    #inlines = [
    #    GuildSettingsInline,
    #]


class UserSettingsInline(admin.TabularInline):
    model = UserSettings


class UserAdmin(admin.ModelAdmin):
    model = DiscordUser,
    inlines = [
        UserSettingsInline,
    ]

    search_fields = ['discord_name']


class GuildSettingsAdmin(admin.ModelAdmin):
    model = GuildSettings

    autocomplete_fields = ['permissions_admins', 'permissions_moderators', 'permissions_trusted', 'permissions_banned']


admin.site.register(DiscordUser, UserAdmin)
admin.site.register(DiscordGuild, GuildAdmin)
admin.site.register(Action)
admin.site.register(GuildSettings, GuildSettingsAdmin)
admin.site.register(APIAccess)
admin.site.register(BotTask)
admin.site.register(RolePersist)
