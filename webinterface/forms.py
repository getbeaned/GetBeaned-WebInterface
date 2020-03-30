from crispy_forms.bootstrap import TabHolder, Tab, Alert
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit, HTML
from django.forms import ModelForm, Textarea, ModelMultipleChoiceField
from .models import DiscordUser, DiscordGuild, Action, GuildSettings, BotTask, RolePersist


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
        fields = ['reason', 'pardonned']

        widgets = {
            'reason': Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class BotTaskForm(ModelForm):
    class Meta:
        model = BotTask
        # include all fields you're saving from the form here
        fields = '__all__'
        exclude = ['completed']


class WebSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-7'
        #self.helper.error_text_inline = False

        self.helper.layout = Layout(
            TabHolder(
                Tab('General',
                    *[Div(field_name) for field_name in ['invite_code',
                                                         'rules',
                                                         'bot_prefix',
                                                         'bot_discret',
                                                         'force_justification_level',
                                                         'logs_security_level',
                                                         ]]
                    ),
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
                                                                 'automod_score_multimessage_too_many_mentions',
                                                                 'automod_score_multimessage_too_many_users_mentions',
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
                                                                 'autotrigger_instantessaydiscordbots_score',
                                                                 'autotrigger_sexbots_score',
                                                                 ]]
                            ),
                        Tab('Misc options',
                            *[Div(field_name) for field_name in ['automod_ignore_level',
                                                                 'automod_minimal_membercount_trust_server',
                                                                 'automod_note_message_deletions',
                                                                 ]]
                            ),
                        ),
                    ),
                Tab('AutoInspect',
                    HTML("""</br><div class="alert alert-info" role="alert">
                                        AutoInspect inspect people profiles for pre-configured patterns and then act on them. This feature is experimental. 
                                        Please go to the support server if you have any questions.</br>

                                        ⚠️ Activating this can kick/ban people when they join, thus limiting their ability to warn you of a misconfiguration.
                                         For this reason, you <strong>MUST</strong> have a configured log channel (AutoInspect logs)
                                      </div>
                                    """),
                    *[Div(field_name) for field_name in ['autoinspect_enable',
                                                         'autoinspect_bypass_enable',
                                                         'autoinspect_bitcoin_bots',
                                                         'autoinspect_pornspam_bots',
                                                         'autoinspect_username',
                                                         'autoinspect_suspicious',
                                                         'autoinspect_antiraid',
                                                         ]]
                    ),
                Tab('DeHoister',
                    *[Div(field_name) for field_name in ['dehoist_enable',
                                                         'dehoist_ignore_level',
                                                         'dehoist_intensity',
                                                         'dehoist_action',
                                                         ]]
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
                                                         'logs_rolepersist_channel_id',
                                                         'logs_member_edits_channel_id',
                                                         'logs_edits_channel_id',
                                                         'logs_delete_channel_id',
                                                         'logs_autoinspect_channel_id',
                                                         ]]
                    ),
                Tab('VIP Settings',
                    HTML("""</br><div class="alert alert-info" role="alert">
                    The settings you can see on this tab are only available to VIP servers. You can edit them, but you'll need a VIP server for them to work.<br/>
                    For more information about VIP servers, please see the <a href='https://docs.getbeaned.me/bot-documentation/vip-servers'>following documentation</a>
                    </div>"""),
                    *[Div(field_name) for field_name in ['rolepersist_enable',
                                                         'rolepersist_default_roles',
                                                         'vip_custom_bad_words_list',
                                                         'vip_custom_bad_regex_list',
                                                         ]],
                    HTML("""</br><div class="alert alert-warning" role="alert">
                            Please test your regexes before submitting the form! Use <a href='https://regex101.com/'>Regex101</a> 
                            to make sure they match what you want, nothing more and nothing less.
                            </div>"""),
                    ),
            )
        )
        self.helper.add_input(Submit('submit', 'Submit'))
        super(WebSettingsForm, self).__init__(*args, **kwargs)

    class Meta:
        model = GuildSettings
        fields = '__all__'
        exclude = ['guild', 'imported_bans', 'vip']
