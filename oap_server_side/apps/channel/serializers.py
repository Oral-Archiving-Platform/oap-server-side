from rest_framework import serializers
from .models import Channel, ChannelMembership, Subscription

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'

class ChannelMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelMembership
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'