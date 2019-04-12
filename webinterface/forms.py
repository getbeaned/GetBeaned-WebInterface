from crispy_forms.bootstrap import TabHolder, Tab, Alert
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit, HTML
from django.forms import ModelForm, Textarea, ModelMultipleChoiceField
from .models import DiscordUser, DiscordGuild, Action, GuildSettings


class DiscordUserForm(ModelForm):
    class Meta:
        model = DiscordUser
        # include all fields you're saving from the form here
        fields = '__all__'
        exclude = ['admin_info']

    def validate_unique(self):
        pass


class DiscordGuildForm(ModelForm):
    class Meta:
        model = DiscordGuild
        # include all fields you're saving from the form here
        fields = '__all__'

    def validate_unique(self):
        pass


class ActionForm(ModelForm):
    class Meta:
        model = Action
        # include all fields you're saving from the form here
        fields = '__all__'
        exclude = ['timestamp']


class ActionEditForm(ModelForm):
    class Meta:
        model = Action
        # include all fields you're saving from the form here
        fields = ['reason']

        widgets = {
            'reason': Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class WebSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-7'
        #self.helper.error_text_inline = False

        self.helper.layout = Layout(
            TabHolder(
                Tab('Automod',
                    TabHolder(
                        Tab('Required totals to act',
                            *[Div(field_name) for field_name in ['automod_enable',
                                                                 'automod_delete_message_score',
                                                                 'automod_warn_score',
                                                                 'automod_kick_score',
                                                                 'automod_softban_score',
                                                                 'automod_ban_score',
                                                                 ]]
                            ),
                        Tab('Users multiplicators',
                            *[Div(field_name) for field_name in ['automod_multiplictor_offline',
                                                                 'automod_multiplictor_new_account',
                                                                 'automod_multiplictor_just_joined',
                                                                 'automod_multiplictor_have_nitro',
                                                                 'automod_multiplictor_have_roles',
                                                                 'automod_multiplictor_bot_banned',
                                                                 ]]
                            ),
                        Tab('Messages scores',
                            *[Div(field_name) for field_name in ['automod_score_caps',
                                                                 'automod_score_embed',
                                                                 'automod_score_everyone',
                                                                 'automod_score_too_many_mentions',
                                                                 'automod_score_contain_invites',
                                                                 'automod_score_repeated',
                                                                 'automod_score_bad_words',
                                                                 'automod_score_zalgo',
                                                                 ]]
                            ),
                        Tab('AutoTrigger',
                            HTML("""</br><div class="alert alert-info" role="alert">
                                      AutoTriggers fire for specific configured messages.</br>
                                      If you find bots spamming in a number of discord servers that aren't well caught by the AutoMod, 
                                      feel free to suggest an AutoTrigger on the support server. </br>
                                      You can disable any of them by setting their score to 0.
                                    </div>
                                """),
                            *[Div(field_name) for field_name in ['autotrigger_enable',
                                                                 'autotrigger_sexdatingdiscordbots_score',
                                                                 'autotrigger_instantessaydiscordbots_score'
                                                                 ]]
                            ),
                        Tab('Misc options',
                            *[Div(field_name) for field_name in ['automod_ignore_level',
                                                                 'automod_ignore_invites_in',
                                                                 'automod_minimal_membercount_trust_server',
                                                                 'automod_note_message_deletions'
                                                                 ]]
                            ),
                        ),
                    ),
                Tab('Thresholds',
                    *[Div(field_name) for field_name in ['thresholds_enable',
                                                         'thresholds_mutes_to_kick',
                                                         'thresholds_warns_to_kick',
                                                         'thresholds_kicks_to_bans',
                                                         'thresholds_softbans_to_bans',
                                                         ]]
                    ),
                Tab('Permissions',
                    *[Div(field_name) for field_name in ['permissions_admins',
                                                         'permissions_moderators',
                                                         'permissions_trusted',
                                                         'permissions_banned',
                                                         ]]
                    ),
                Tab('Logs',
                    *[Div(field_name) for field_name in ['logs_enable',
                                                         'logs_as_embed',
                                                         'logs_moderation_channel_id',
                                                         'logs_joins_channel_id',
                                                         'logs_member_edits_channel_id',
                                                         'logs_edits_channel_id',
                                                         'logs_delete_channel_id',
                                                         ]]
                    ),
                Tab('Misc',
                    *[Div(field_name) for field_name in ['bot_prefix',
                                                         ]]
                    ),

            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))
        super(WebSettingsForm, self).__init__(*args, **kwargs)

    class Meta:
        model = GuildSettings
        fields = '__all__'
        exclude = ['guild', 'imported_bans']
