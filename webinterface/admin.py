from django.contrib import admin
from .models import DiscordUser, DiscordGuild, Action, APIAccess, GuildSettings, UserSettings


# Register your models here.

class GuildSettingsInline(admin.TabularInline):
    model = GuildSettings


class GuildAdmin(admin.ModelAdmin):
    inlines = [
        GuildSettingsInline,
    ]


class UserSettingsInline(admin.TabularInline):
    model = UserSettings


class UserAdmin(admin.ModelAdmin):
    inlines = [
        UserSettingsInline,
    ]


admin.site.register(DiscordUser, UserAdmin)
admin.site.register(DiscordGuild, GuildAdmin)
admin.site.register(Action)
admin.site.register(GuildSettings)
admin.site.register(APIAccess)
