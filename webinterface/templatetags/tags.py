from django import template
from webinterface.edition_controls import can_edit as can_edit_test
register = template.Library()


@register.inclusion_tag('parts/card.html')
def show_card(user, card, show_details_button=True, edit_form=None):
    return {'action': card, 'show_details_button':show_details_button,
            'edit_form':edit_form, 'user':user}


@register.filter()
def can_edit(who, what):
    return can_edit_test(who, what)
