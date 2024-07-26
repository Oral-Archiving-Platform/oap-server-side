from django.contrib import admin
from .models import Channel, ChannelMembership, Subscription
# Register your models here.

admin.site.register(Channel)
admin.site.register(ChannelMembership)
admin.site.register(Subscription)