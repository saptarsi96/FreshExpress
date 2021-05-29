from django import template
from store.models import Merchant

register = template.Library()

@register.filter(name="ismerchant")
def ismerchat(user):
    if Merchant.objects.filter(user=user).exists():
        return True
    return False