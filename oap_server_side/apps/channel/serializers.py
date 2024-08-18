from rest_framework import serializers
from .models import Channel, ChannelMembership, Subscription
from apps.users.serializers import UserSerializer
from django.db import transaction
from django.db import IntegrityError

class ChannelSerializer(serializers.ModelSerializer):
    subscription_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Channel
        fields = ['id', 'name', 'description', 'creationDate', 'icon', 'cover','subscription_count']
        read_only_fields = ['id', 'creationDate']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        channel = Channel.objects.create(**validated_data)
        ChannelMembership.objects.create(
            channelID=channel,
            userID=user,
            role=ChannelMembership.OWNER
        )
        return channel
    def get_subscription_count(self, obj):
        return Subscription.objects.filter(channelID=obj).count()



class ChannelMembershipSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(source='channelID', read_only=True)
    user = UserSerializer(source='userID', read_only=True)

    class Meta:
        model = ChannelMembership
        fields = ['id', 'channel', 'user', 'role', 'channelID', 'userID']
        read_only_fields = ['id']
        extra_kwargs = {
            'channelID': {'write_only': True},
            'userID': {'write_only': True}
        }
    




class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['id', 'subscriptionDate','userID']